const util = require('util');
const exec = util.promisify(require('child_process').exec);
const JiraApi = require('jira-client');
require('colors');
const program = require('commander');

program
  .version('1.0')
  .option('-r, --rbtUser [rbtUser]', 'The Review Board user')
  .option('-j --jiraUser [jiraUser]', 'The Jira user')
  .option('-p --jiraPassword [jiraPassword]', 'The Jira password')
  .option(
    '-h --huePath [huePath]',
    'The path to the Hue folder, if not set it will be ../../ relative to the tool (optional)'
  )
  .option('-d --dryRun', 'Will not update any Jiras (optional)')
  .parse(process.argv);

const missing = [];
if (!program.rbtUser) {
  missing.push('rbtUser');
}

if (!program.jiraUser) {
  missing.push('jiraUser');
}

if (!program.jiraPassword) {
  missing.push('jiraPassword');
}

if (missing.length) {
  // eslint-disable-next-line no-restricted-syntax
  console.log(`\nThe following required arguments are missing:\n  ${missing.join('\n  ').red}\n`);
  program.help();
}

const getPendingReviews = async user => {
  const { stdout, stderr } = await exec(
    `rbt api-get --server=https://review.cloudera.org /review-requests/ --from-user=${user} --status=pending --max-results=20`
  );
  if (stderr) {
    throw new Error(stderr);
  }
  return JSON.parse(stdout).review_requests;
};

const getCommits = async (jira, huePath) => {
  const { stdout, stderr } = await exec(
    `pushd ${huePath} > /dev/null && git log origin/master --grep=${jira}  --format=https://github.com/cloudera/hue/commit/%H | tail -r && popd > /dev/null`
  );
  if (stderr) {
    throw new Error(stderr);
  }
  if (!stdout.trim()) {
    return [];
  }
  return stdout.trim().split('\n');
};

const extractJiras = reviews => {
  const jiraIndex = {};

  reviews.forEach(review => {
    const matches = review.description.match(/(HUE-[0-9]+)/gi);
    if (matches) {
      matches.forEach(jira => {
        const upperJira = jira.toUpperCase();
        if (!jiraIndex[upperJira]) {
          jiraIndex[upperJira] = { reviewUrls: {} };
        }
        jiraIndex[upperJira].reviewUrls[review.absolute_url] = true;
      });
    }
  });

  const result = [];
  Object.keys(jiraIndex).forEach(jiraNumber => {
    const urls = Object.keys(jiraIndex[jiraNumber].reviewUrls);
    urls.sort();
    result.push({
      jira: jiraNumber,
      reviews: urls
    });
  });
  result.sort((a, b) => {
    return a.jira.localeCompare(b.jira);
  });
  return result;
};

const asyncForEach = async (array, callback) => {
  for (let index = 0; index < array.length; index++) {
    await callback(array[index], index, array);
  }
};

const jiraApi = new JiraApi({
  protocol: 'https',
  host: 'issues.cloudera.org/',
  username: program.jiraUser,
  password: program.jiraPassword,
  apiVersion: '2',
  strictSSL: true
});

const fetchExistingJira = async jiraNumber => {
  const existingJira = await jiraApi.findIssue(jiraNumber, undefined, 'comment, status');
  if (
    !existingJira ||
    !existingJira.fields ||
    !existingJira.fields.comment ||
    !existingJira.fields.status
  ) {
    throw new Error('Returned Jira has no comment or status fields.');
  }
  return existingJira;
};

const extractJiraComment = existingJira => {
  if (existingJira.fields.comment.comments) {
    return existingJira.fields.comment.comments.reduce(
      (val, comment) => val + comment.body + '\n',
      ''
    );
  }
  return '';
};

const hasOpenStatus = existingJira => existingJira.fields.status.id === '1';

const generateComment = (commitUrls, reviewUrls) => {
  let comment = '';
  if (reviewUrls.length) {
    comment += reviewUrls.length > 1 ? 'Reviews:\n' : 'Review:\n';
    comment += reviewUrls.join('\n');
  }
  if (commitUrls.length) {
    if (comment) {
      comment += '\n\n';
    }
    comment += commitUrls.length > 1 ? 'Commits:\n' : 'Commit:\n';
    comment += commitUrls.join('\n');
  }
  return comment;
};

const transitionJiraToInProgress = async jira => {
  await jiraApi.transitionIssue(jira.key, { transition: { id: 4 } });
};

const updateExistingJira = async reviewJiras => {
  let updatedJiraCount = 0;
  await asyncForEach(reviewJiras, async reviewJira => {
    const missingCommitUrls = [];
    const missingReviewUrls = [];
    const existingJira = await fetchExistingJira(reviewJira.jira);

    const existingComment = extractJiraComment(existingJira).toLowerCase();
    reviewJira.reviews.forEach(review => {
      if (existingComment.indexOf(review.toLowerCase()) === -1) {
        missingReviewUrls.push(review);
      }
    });
    reviewJira.commits.forEach(commit => {
      if (existingComment.indexOf(commit.toLowerCase()) === -1) {
        missingCommitUrls.push(commit);
      }
    });
    if (missingCommitUrls.length || missingReviewUrls.length) {
      const comment = generateComment(missingCommitUrls, missingReviewUrls);
      // eslint-disable-next-line no-restricted-syntax
      console.log(`\nAdding comment to ${existingJira.key}...\n`.cyan);
      // eslint-disable-next-line no-restricted-syntax
      console.log(comment);
      updatedJiraCount++;
      if (!program.dryRun) {
        await jiraApi.addComment(existingJira.key, comment);
      }
      if (hasOpenStatus(existingJira)) {
        // eslint-disable-next-line no-restricted-syntax
        console.log(`\nTransitioning ${existingJira.key} to 'In Progress'...\n`.cyan);
        if (!program.dryRun) {
          await transitionJiraToInProgress(existingJira);
        }
      }
    }
  });
  return updatedJiraCount;
};

const HUE_PATH = program.huePath || `${__dirname}/../../`;

const linkCommits = async reviewJiras => {
  await asyncForEach(reviewJiras, async reviewJira => {
    reviewJira.commits = await getCommits(reviewJira.jira, HUE_PATH);
  });
};

const main = async () => {
  // Fetch the reviews using rbt cli
  const reviews = await getPendingReviews(program.rbtUser);

  // Extract jira information form the reviews
  const reviewJiras = extractJiras(reviews);

  // Use git log orgin/master and link commits to the jiras from the reviews
  await linkCommits(reviewJiras);

  // Update the actual jira with missing review and commit urls
  const updatedJiraCount = await updateExistingJira(reviewJiras);

  if (updatedJiraCount) {
    // eslint-disable-next-line no-restricted-syntax
    console.log(
      `\nUpdated ${updatedJiraCount} jira(s)${program.dryRun ? ' (dry run)'.gray : ''}`.green
    );
  } else {
    // eslint-disable-next-line no-restricted-syntax
    console.log('\nNothing to update.\n'.green);
  }
};

try {
  main();
} catch (err) {
  console.error(err);
}
