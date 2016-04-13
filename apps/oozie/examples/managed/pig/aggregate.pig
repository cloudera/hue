
A = LOAD '$INPUT' AS (word:CHARARRAY, count:INT);

B = FOREACH A GENERATE count, word;
C = ORDER B BY count DESC;

STORE C INTO '$OUTPUT';

