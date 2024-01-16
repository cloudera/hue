import {
  withGuardrails,
  GuardrailAlertType,
  invalidAiResponseMsg,
  invalidAiResponseTitle,
  syntaxErrorWarning,
  deleteWarning,
  alterWarning,
  cteWarning,
  defaultKeywordWarning,
  hallucinationWarning,
  hallucinationWarningTitle,
  missingTableWarning,
  missingColumnWarning,
  rephrasActionMsg,
  exploreActionMsg
} from './guardRails';

describe('withGuardrails', () => {
  it('returns complete API response except "tableColumnsMetadata" for successful calls', async () => {
    // SQL + ASSUMPTIONS
    const mockApiResponse = {
      sql: 'SELECT col1 FROM table1',
      assumptions: 'here is my assumption',
      tableColumnsMetadata: [{ name: 'table1', columns: [{ name: 'col1' }] }]
    };
    const mockFunctionToGuard = jest.fn().mockReturnValue(mockApiResponse);
    const result = await withGuardrails(mockFunctionToGuard)({
      dialect: 'hive'
    });
    const { sql, assumptions } = mockApiResponse;
    expect(result).toEqual({ sql, assumptions });

    // SQL + EXPLAIN
    const mockApiResponse2 = {
      sql: 'SELECT col1 FROM table1',
      explain: 'here is my explain',
      tableColumnsMetadata: [{ name: 'table1', columns: [{ name: 'col1' }] }]
    };
    const mockFunctionToGuard2 = jest.fn().mockReturnValue(mockApiResponse2);
    const result2 = await withGuardrails(mockFunctionToGuard2)({
      dialect: 'hive'
    });
    expect(result2).toEqual({ sql: mockApiResponse2.sql, explain: mockApiResponse2.explain });

    // EXPLAIN + SUMMARY
    const mockApiResponse3 = {
      summary: 'SELECT col1 FROM table1',
      explain: 'here is my explain'
    };
    const mockFunctionToGuard3 = jest.fn().mockReturnValue(mockApiResponse3);
    const result3 = await withGuardrails(mockFunctionToGuard3)({
      dialect: 'hive'
    });
    expect(result3).toEqual({
      explain: mockApiResponse3.explain,
      summary: mockApiResponse3.summary
    });
  });

  it('does not on warn on read only statements', async () => {
    const select = await withGuardrails(async () => ({
      sql: 'SELECT col1 FROM table1;'
    }))({
      dialect: 'hive'
    });
    expect(select.guardrailAlert).toBeUndefined();

    const decribe = await withGuardrails(async () => ({
      sql: 'DESCRIBE table1;'
    }))({
      dialect: 'hive'
    });
    expect(decribe.guardrailAlert).toBeUndefined();

    const show = await withGuardrails(async () => ({
      sql: 'SHOW TABLES;'
    }))({
      dialect: 'hive'
    });
    expect(show.guardrailAlert).toBeUndefined();
  });

  it('correctly handles HIVE specific queries', async () => {
    const mockApiResponse = {
      sql: 'SELECT col1 FROM table1 LATERAL VIEW explode(col2) exploded_table AS address;',
      assumptions: 'here is my assumption',
      tableColumnsMetadata: [{ name: 'table1', columns: [{ name: 'col1' }, { name: 'col2' }] }]
    };
    const mockFunctionToGuard = jest.fn().mockReturnValue(mockApiResponse);

    const resultUsingHive = await withGuardrails(mockFunctionToGuard)({
      dialect: 'hive'
    });
    const { sql, assumptions } = mockApiResponse;
    expect(resultUsingHive.guardrailAlert).not.toBeDefined();
    expect(resultUsingHive).toEqual({ sql, assumptions });

    const resultUsingOtherParser = await withGuardrails(mockFunctionToGuard)({
      dialect: 'spark'
    });

    expect(resultUsingOtherParser.guardrailAlert).toBeDefined();
    expect(resultUsingOtherParser.guardrailAlert.type).toEqual(GuardrailAlertType.SYNTAX_ERROR);
  });

  it('correctly handles IMPALA specific queries', async () => {
    const mockApiResponse = {
      sql: 'SHOW TABLE STATS table1;',
      assumptions: 'here is my assumption',
      tableColumnsMetadata: [{ name: 'table1', columns: [{ name: 'col1' }, { name: 'col2' }] }]
    };
    const mockFunctionToGuard = jest.fn().mockReturnValue(mockApiResponse);

    const resultUsingImpala = await withGuardrails(mockFunctionToGuard)({
      dialect: 'impala'
    });
    const { sql, assumptions } = mockApiResponse;
    expect(resultUsingImpala.guardrailAlert).not.toBeDefined();
    expect(resultUsingImpala).toEqual({ sql, assumptions });

    const resultUsingOtherParser = await withGuardrails(mockFunctionToGuard)({
      dialect: 'spark'
    });

    expect(resultUsingOtherParser.guardrailAlert).toBeDefined();
    expect(resultUsingOtherParser.guardrailAlert.type).toEqual(GuardrailAlertType.SYNTAX_ERROR);
  });

  it('warns on invalid AI response', async () => {
    const mockApiResponse = {
      sql: '',
      assumptions: '',
      tableColumnsMetadata: [{ name: 'table1', columns: [{ name: 'col1' }] }]
    };
    const mockFunctionToGuard = jest.fn().mockReturnValue(mockApiResponse);
    const result = await withGuardrails(mockFunctionToGuard)({
      dialect: 'hive'
    });

    expect(result.guardrailAlert.type).toEqual(GuardrailAlertType.INVALID_AI_RESPONSE);
    expect(result.guardrailAlert.msg).toEqual(invalidAiResponseMsg);
    expect(result.guardrailAlert.title).toEqual(invalidAiResponseTitle);
  });

  it('warns on SQL with syntax error', async () => {
    const mockApiResponse = {
      sql: 'SELET * from table1;',
      assumptions: 'here is my assumption',
      tableColumnsMetadata: [{ name: 'table1', columns: [{ name: 'col1' }, { name: 'col2' }] }]
    };
    const mockFunctionToGuard = jest.fn().mockReturnValue(mockApiResponse);

    const result = await withGuardrails(mockFunctionToGuard)({
      dialect: 'hive'
    });

    expect(result.guardrailAlert).toBeDefined();
    expect(result.guardrailAlert.type).toEqual(GuardrailAlertType.SYNTAX_ERROR);
    expect(result.guardrailAlert.confirmationText).toEqual(syntaxErrorWarning('SELET', 1, 5));
  });

  it('warns on unsafe SQL that deletes data ', async () => {
    const mockApiResponse = {
      sql: 'DELETE FROM table1 WHERE col1 = 5;',
      assumptions: 'here is my assumption',
      tableColumnsMetadata: [{ name: 'table1', columns: [{ name: 'col1' }, { name: 'col2' }] }]
    };
    const mockFunctionToGuard = jest.fn().mockReturnValue(mockApiResponse);

    const result = await withGuardrails(mockFunctionToGuard)({
      dialect: 'hive',
      nql: 'Do forbidden stuff'
    });

    expect(result.guardrailAlert).toBeDefined();
    expect(result.guardrailAlert.type).toEqual(GuardrailAlertType.UNSAFE_SQL);
    expect(result.guardrailAlert.confirmationText).toEqual(deleteWarning('DELETE'));
    expect(result.guardrailAlert.nql).toEqual('Do forbidden stuff');

    // CHECKING FOR UNSAFE SQL HAS PRECEDENCE OVER HALLUCIANATION CHECK
    // SO WE DON'T HAVE TO ADD tableColumnsMetadata WHEN WE TEST THE OTHER KEYWORDS
    const truncate = await withGuardrails(async () => ({ sql: 'TRUNCATE TABLE tablename;' }))({
      dialect: 'hive'
    });
    expect(truncate.guardrailAlert.type).toEqual(GuardrailAlertType.UNSAFE_SQL);
    expect(truncate.guardrailAlert.confirmationText).toEqual(deleteWarning('TRUNCATE'));

    const drop = await withGuardrails(async () => ({ sql: 'DROP TABLE tablename;' }))({
      dialect: 'hive'
    });
    expect(drop.guardrailAlert.type).toEqual(GuardrailAlertType.UNSAFE_SQL);
    expect(drop.guardrailAlert.confirmationText).toEqual(deleteWarning('DROP'));
  });

  it('warns on unsafe SQL that alters data ', async () => {
    const mockApiResponse = {
      sql: 'ALTER TABLE table1 ADD COLUMNS (birth_date DATE);',
      assumptions: 'here is my assumption',
      tableColumnsMetadata: [{ name: 'table1', columns: [{ name: 'col1' }, { name: 'col2' }] }]
    };
    const mockFunctionToGuard = jest.fn().mockReturnValue(mockApiResponse);

    const result = await withGuardrails(mockFunctionToGuard)({
      dialect: 'hive',
      nql: 'Delete some stuff'
    });

    expect(result.guardrailAlert).toBeDefined();
    expect(result.guardrailAlert.type).toEqual(GuardrailAlertType.UNSAFE_SQL);
    expect(result.guardrailAlert.confirmationText).toEqual(alterWarning('ALTER'));

    // CHECKING FOR UNSAFE SQL HAS PRECEDENCE OVER HALLUCIANATION CHECK
    // SO WE DON'T HAVE TO ADD tableColumnsMetadata WHEN WE TEST THE OTHER KEYWORDS
    const insert = await withGuardrails(async () => ({
      sql: `INSERT INTO TABLE table1 VALUES ('my new value');`
    }))({
      dialect: 'hive'
    });
    expect(insert.guardrailAlert.type).toEqual(GuardrailAlertType.UNSAFE_SQL);
    expect(insert.guardrailAlert.confirmationText).toEqual(alterWarning('INSERT'));

    const update = await withGuardrails(async () => ({
      sql: 'UPDATE table1 SET col1 = 10;'
    }))({
      dialect: 'hive'
    });
    expect(update.guardrailAlert.type).toEqual(GuardrailAlertType.UNSAFE_SQL);
    expect(update.guardrailAlert.confirmationText).toEqual(alterWarning('UPDATE'));

    const load = await withGuardrails(async () => ({
      sql: `LOAD DATA LOCAL INPATH '/local/path/to/input/data' INTO TABLE tablename;`
    }))({
      dialect: 'hive'
    });
    expect(load.guardrailAlert.type).toEqual(GuardrailAlertType.UNSAFE_SQL);
    expect(load.guardrailAlert.confirmationText).toEqual(alterWarning('LOAD'));

    const merge = await withGuardrails(async () => ({
      sql: `MERGE INTO target_table AS T USING source_table AS S ON T.id = S.id
      WHEN MATCHED THEN UPDATE SET T.name = S.name WHEN NOT MATCHED THEN INSERT VALUES (S.id, S.name);`
    }))({
      dialect: 'hive'
    });
    expect(merge.guardrailAlert.type).toEqual(GuardrailAlertType.UNSAFE_SQL);
    expect(merge.guardrailAlert.confirmationText).toEqual(alterWarning('MERGE'));

    const upsert = await withGuardrails(async () => ({
      sql: `UPSERT INTO employees (id, name, email) VALUES (2, ‘Dennis’, syland.corp’
        );`
    }))({
      dialect: 'impala'
    });
    expect(upsert.guardrailAlert.type).toEqual(GuardrailAlertType.UNSAFE_SQL);
    expect(upsert.guardrailAlert.confirmationText).toEqual(alterWarning('UPSERT'));
  });

  it('warns on SQL using CTE since it is not properly parsed and cant be checked', async () => {
    const mockApiResponse = {
      sql: `with table2 as ( select * from table1)
      select * from table2`
    };
    const mockFunctionToGuard = jest.fn().mockReturnValue(mockApiResponse);

    const result = await withGuardrails(mockFunctionToGuard)({
      dialect: 'hive'
    });

    expect(result.guardrailAlert).toBeDefined();
    expect(result.guardrailAlert.type).toEqual(GuardrailAlertType.UNSAFE_SQL);
    expect(result.guardrailAlert.confirmationText).toEqual(cteWarning);
  });

  it('warns on SQL that is not read only using a default warning msg', async () => {
    const mockApiResponse = {
      sql: 'CREATE TABLE mytable (id INT);'
    };
    const mockFunctionToGuard = jest.fn().mockReturnValue(mockApiResponse);

    const result = await withGuardrails(mockFunctionToGuard)({
      dialect: 'hive'
    });

    expect(result.guardrailAlert).toBeDefined();
    expect(result.guardrailAlert.type).toEqual(GuardrailAlertType.UNSAFE_SQL);
    expect(result.guardrailAlert.confirmationText).toEqual(defaultKeywordWarning('CREATE'));
  });

  it('should warn on SQL table name hallucinations', async () => {
    const mockApiResponse = {
      sql: 'Select * from table2',
      assumptions: 'here is my assumption',
      tableColumnsMetadata: [{ name: 'table1', columns: [{ name: 'col1' }] }]
    };
    const mockFunctionToGuard = jest.fn().mockReturnValue(mockApiResponse);

    const result = await withGuardrails(mockFunctionToGuard)({
      dialect: 'hive'
    });

    expect(result.guardrailAlert).toBeDefined();
    expect(result.guardrailAlert.type).toEqual(GuardrailAlertType.HALLUCINATION);
    expect(result.guardrailAlert.confirmationText).toEqual(hallucinationWarning);
    expect(result.guardrailAlert.title).toEqual(hallucinationWarningTitle);
    expect(result.guardrailAlert.msg.trim()).toEqual(missingTableWarning('table2'));
  });

  it('should warn on SQL column name hallucinations', async () => {
    const mockApiResponse = {
      sql: 'Select col2 from table1',
      assumptions: 'here is my assumption',
      tableColumnsMetadata: [{ name: 'table1', columns: [{ name: 'col1' }] }]
    };
    const mockFunctionToGuard = jest.fn().mockReturnValue(mockApiResponse);

    const result = await withGuardrails(mockFunctionToGuard)({
      dialect: 'hive'
    });

    expect(result.guardrailAlert).toBeDefined();
    expect(result.guardrailAlert.type).toEqual(GuardrailAlertType.HALLUCINATION);
    expect(result.guardrailAlert.confirmationText).toEqual(hallucinationWarning);
    expect(result.guardrailAlert.title).toEqual(hallucinationWarningTitle);
    expect(result.guardrailAlert.msg.trim()).toEqual(missingColumnWarning('col2'));
  });

  it('suggests possible actions on SQL hallucinations', async () => {
    const mockApiResponse = {
      sql: 'Select * from table2',
      assumptions: 'here is my assumption',
      tableColumnsMetadata: [{ name: 'table1', columns: [{ name: 'col1' }] }]
    };
    const mockFunctionToGuard = jest.fn().mockReturnValue(mockApiResponse);

    const result = await withGuardrails(mockFunctionToGuard)({
      dialect: 'hive'
    });
    expect(result.guardrailAlert.actions).toBeDefined();
    expect(result.guardrailAlert.actions).toContain(exploreActionMsg);
    expect(result.guardrailAlert.actions).toContain(rephrasActionMsg);
  });
});
