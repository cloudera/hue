// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.dao;

import org.jdbi.v3.sqlobject.config.RegisterBeanMapper;
import org.jdbi.v3.sqlobject.customizer.Bind;
import org.jdbi.v3.sqlobject.customizer.BindBean;
import org.jdbi.v3.sqlobject.customizer.Define;
import org.jdbi.v3.sqlobject.statement.GetGeneratedKeys;
import org.jdbi.v3.sqlobject.statement.SqlQuery;
import org.jdbi.v3.sqlobject.statement.SqlUpdate;
import org.jdbi.v3.stringtemplate4.UseStringTemplateEngine;

import com.cloudera.hue.querystore.common.dto.FacetEntry;
import com.cloudera.hue.querystore.common.entities.ImpalaQueryEntity;
import com.cloudera.hue.querystore.common.repository.JdbiDao;

import java.util.Collection;
import java.util.List;
import java.util.Optional;

/**
 * Jdbi dao for ImpalaQueryEntity
 */
@RegisterBeanMapper(ImpalaQueryEntity.class)
public interface ImpalaQueryDao extends JdbiDao<ImpalaQueryEntity> {
  @Override
  @SqlQuery("select * from impala_query")
  Collection<ImpalaQueryEntity> findAll();

  @Override
  @SqlQuery("select * from impala_query where id = :id")
  Optional<ImpalaQueryEntity> findOne(@Bind("id") long id);

  @SqlQuery("select * from impala_query where query_id = :queryId")
  Optional<ImpalaQueryEntity> findByQueryId(@Bind("queryId") String queryId);

  @Override
  @SqlUpdate("insert into impala_query (query_id,query_text,status,query_type," +
      "start_time,end_time,duration,user_name,coordinator," +
      "cpu_time,rows_produced,peak_memory,hdfs_bytes_read,source_files,version) " +
      "values " +
      "(:queryId,:queryText,:status,:queryType,:startTime,:endTime,:duration," +
      ":userName,:coordinator,:cpuTime,:rowsProduced,:peakMemory,:hdfsBytesRead,:sourceFiles,0)")
  @GetGeneratedKeys
  long insert(@BindBean ImpalaQueryEntity entity);

  @Override
  @SqlUpdate("update impala_query set query_id = :queryId, query_text = :queryText, " +
      "status = :status, query_type = :queryType, start_time = :startTime, end_time = :endTime, " +
      "duration = :duration, user_name = :userName, coordinator = :coordinator, cpu_time = :cpuTime, " +
      "rows_produced = :rowsProduced, peak_memory = :peakMemory, hdfs_bytes_read = :hdfsBytesRead, " +
      "source_files = :sourceFiles, version = :version + 1 " +
      "where id = :id and version = :version" )
  int update(@BindBean ImpalaQueryEntity query);

  @Override
  @SqlUpdate("delete from impala_query where id = :id")
  int delete(@Bind("id") long id);

  @SqlUpdate("delete from impala_query where start_time < :startTime")
  int deleteOlder(@Bind("startTime") long startTime);

  @SqlUpdate("vacuum full impala_query")
  int purge();

  @RegisterBeanMapper(FacetEntry.class)
  @SqlQuery("select <facetField> as key, count(<facetField>) as value from impala_query " +
      "where start_time >= :startTime AND start_time \\<= :endTime " +
      "<if(userCheck)> AND request_user = :userName <endif> " +
      "GROUP BY <facetField> " +
      "ORDER BY count(<facetField>) DESC LIMIT :facetsResultLimit")
  @UseStringTemplateEngine
  List<FacetEntry> getFacetValues(@Define("facetField") String facetField,
      @Bind("startTime") long startTime, @Bind("endTime") long endTime,
      @Bind("userName") String userName, @Define("userCheck") boolean userCheck,
      @Bind("facetsResultLimit") int facetsResultLimit);
}
