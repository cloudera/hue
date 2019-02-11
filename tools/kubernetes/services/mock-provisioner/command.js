
const util = require('util');
const exec = util.promisify(require('child_process').exec);

var exports = module.exports = {};

exports.runCommand = async function(command) {
    console.log("Running shell command: " + command);
    const { stdout, stderr } = await exec(command, { shell: true });
    if (stderr != "") {
        console.error(`error running ${command}: ${stderr}`);
    }
};
