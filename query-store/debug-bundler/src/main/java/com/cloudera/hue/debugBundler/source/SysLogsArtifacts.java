// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.

package com.cloudera.hue.debugBundler.source;

import java.io.IOException;
import java.io.OutputStream;
import java.io.PrintWriter;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Collections;
import java.util.Date;
import java.util.List;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;
import org.apache.hadoop.security.UserGroupInformation;

import com.cloudera.hue.debugBundler.framework.Artifact;
import com.cloudera.hue.debugBundler.framework.ArtifactDownloadException;
import com.cloudera.hue.debugBundler.framework.ArtifactSource;
import com.cloudera.hue.debugBundler.framework.Params;
import com.cloudera.hue.debugBundler.framework.ZipStream;
import com.cloudera.hue.querystore.common.config.DasConfiguration;
import com.cloudera.hue.querystore.common.config.DasConfiguration.ConfVar;
import com.cloudera.hue.querystore.common.entities.HiveQueryBasicInfo;
import com.cloudera.hue.querystore.common.entities.HiveQueryExtendedInfo;
import com.cloudera.hue.querystore.common.repository.HiveQueryBasicInfoRepository;
import com.cloudera.hue.querystore.common.repository.HiveQueryExtendedInfoRepository;
import com.cloudera.hue.querystore.common.util.HiveExecutor;
import com.google.inject.Inject;

import lombok.extern.slf4j.Slf4j;

@Slf4j
public class SysLogsArtifacts implements ArtifactSource {
  private static final ConfVar<Integer> DEBUG_BUNDLER_QUERY_WINDOW_MARGIN_CONF =
      new ConfVar<>("hue.query-processor.debug-bunder.query-window-margin", 60000);

  private static final String COMPUTE_CONFIG_NAME = "hive.llap.task.scheduler.am.registry";

  private static final String DATABASE_NAME = "sys";
  private static final String TABLE_NAME = "logs";

  // DateFormat objects are not thread safe, hence an instance variable.
  private final DateFormat TIME_FORMATTER = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
  private final DateFormat DATE_FORMATTER = new SimpleDateFormat("yyyy-MM-dd");

  private final HiveQueryBasicInfoRepository hiveQueryBasicRepo;
  private final HiveQueryExtendedInfoRepository hiveQueryExtRepo;
  private final DasConfiguration configuration;

  private final int timeWindowMargin;

  /** Testing tips
    1. Add "log.source": "K8S" under dasConf

    Create dummy logs table by running the folowing under sys DB

    2. CREATE TABLE logs (facility STRING, severity STRING, version STRING, hostname STRING, app_name STRING, proc_id STRING, msg_id STRING, ns STRING, app STRING,
          msg BINARY, unmatched BINARY,
          dt DATE, ts TIMESTAMP, structured_data MAP<STRING, STRING>);

    3. INSERT INTO TABLE sys.logs
          (facility, severity, version, hostname, app_name, proc_id, msg_id, app, ns, dt, ts, structured_data)
          SELECT
          "facility3", "severity3", "v1", "hostname3", "app_name3", "proc_id3", "msg_id3", "app", -- Can change at will
          "llap",                -- Must be always llap
          '2020-03-27',          -- Use your query end date, in yyyy-MM-dd format
          '2020-03-27 01:30:00', -- Use your query end time, in yyyy-MM-dd HH:mm:ss format
          MAP('queryId', 'hive_20200326200358_f49dab63-5a5a-4c3f-9aa2-17129b99c955'); -- Use your query Id
  */

  @Inject
  public SysLogsArtifacts(HiveQueryBasicInfoRepository hiveQueryBasicRepo,
      HiveQueryExtendedInfoRepository hiveQueryExtRepo, DasConfiguration configuration) {
    this.hiveQueryBasicRepo = hiveQueryBasicRepo;
    this.hiveQueryExtRepo = hiveQueryExtRepo;
    this.configuration = configuration;

    timeWindowMargin = configuration.getConf(DEBUG_BUNDLER_QUERY_WINDOW_MARGIN_CONF);
  }

  private void streamCSV(ResultSet resultSet, OutputStream outputStream) throws IOException, SQLException {
    ResultSetMetaData metaData = resultSet.getMetaData();
    try (CSVPrinter csvPrinter = new CSVPrinter(new PrintWriter(outputStream), CSVFormat.DEFAULT)) {
      int columns = metaData.getColumnCount();
      for (int i = 0; i < columns; ++i) {
        csvPrinter.print(metaData.getColumnName(i));
      }
      csvPrinter.println();
      while (resultSet.next()) {
        for (int i = 1; i <= columns; ++i) {
          csvPrinter.print(resultSet.getObject(i));
        }
        csvPrinter.println();
      }
      csvPrinter.flush();
    }
  }

  private String constructHiveQuery(HiveQueryBasicInfo query, HiveQueryExtendedInfo queryDetails) {
    Date startTime = new Date(query.getStartTime() - timeWindowMargin);
    Date endTime = new Date(query.getEndTime() + timeWindowMargin);

    String computeName = queryDetails.getConfiguration().get(COMPUTE_CONFIG_NAME).asText();
    String queryId = query.getQueryId();

    return "select facility, severity, version, ts, hostname, app_name, proc_id, msg_id, dt, ns, app, " +
      " structured_data," +
      " decode(msg,'UTF-8') as msg," +
      " decode(unmatched,'UTF-8') as unmatched " +
      " from " + DATABASE_NAME + "." + TABLE_NAME +
      " where structured_data['queryId'] = '" + queryId + "'" +
      " and dt BETWEEN '" + DATE_FORMATTER.format(startTime) + "' AND '" + DATE_FORMATTER.format(endTime) + "'" +
      " and ts BETWEEN '" + TIME_FORMATTER.format(startTime) + "' AND '" + TIME_FORMATTER.format(endTime) + "'" +
      " and ns = '" + computeName + "'";
  }

  @Override
  public List<Artifact> getArtifacts(Params params) {
    return Collections.singletonList(new Artifact() {
      @Override
      public String getName() {
        return "SYS_LOGS.csv";
      }

      @Override
      public Object getData() throws ArtifactDownloadException {
        return null;
      }

      @Override
      public Object getContext() {
        return null;
      }
    });
  }

  @Override
  public void process(Params params, Artifact artifact, ZipStream zipStream) throws ArtifactDownloadException {
    String queryId = params.getHiveQueryId();
    HiveQueryBasicInfo query = hiveQueryBasicRepo.findByHiveQueryId(queryId).get();
    HiveQueryExtendedInfo queryDetails = hiveQueryExtRepo.findByHiveQueryId(queryId).get();

    HiveExecutor executor = new HiveExecutor(configuration);
    String logQuery = constructHiveQuery(query, queryDetails);
    log.debug("Executing Hive query to extract logs: " + logQuery);
    try {
      // Login user is used to read the sys tables. The end user may not have access to sys tables and we have validated
      // that the user can access the logs in the resource.
      String loginUser = UserGroupInformation.getLoginUser().getShortUserName();
      executor.executeQuery(logQuery, loginUser, rs -> {
        try (OutputStream fileStream = zipStream.openFile(artifact.getName())) {
          streamCSV(rs, fileStream);
          return true;
        } catch (IOException e) {
          throw new SQLException(e);
        }
      });
    } catch (SQLException | IOException e) {
      throw new ArtifactDownloadException(e);
    }
  }

  @Override
  public boolean hasRequiredParams(Params params) {
    return params.getHiveQueryId() != null;
  }

}
