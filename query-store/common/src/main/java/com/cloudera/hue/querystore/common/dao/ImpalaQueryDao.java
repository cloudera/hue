// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.dao;

import org.jdbi.v3.sqlobject.config.RegisterBeanMapper;
import org.jdbi.v3.sqlobject.customizer.Bind;
import org.jdbi.v3.sqlobject.customizer.BindBean;
import org.jdbi.v3.sqlobject.customizer.BindList;
import org.jdbi.v3.sqlobject.customizer.Define;
import org.jdbi.v3.sqlobject.customizer.BindList.EmptyHandling;
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

  @SqlQuery(
    "select * from impala_query " +
    "where start_time >= :startTime AND start_time \\<= :endTime " +
    "<if(checkCurrentUser)>AND user_name = :currentUser <endif> " +

    "<if(checkText)>AND (query_id = :text OR query_text LIKE :queryText) <endif>" +

    "<if(checkStatus)>AND status in (<statuses>) <endif>" +
    "<if(checkQueryType)>AND query_type in (<queryTypes>) <endif>" +
    "<if(checkUserNames)>AND user_name in (<userNames>) <endif>" +
    "<if(checkCoordinator)>AND coordinator in (<coordinators>) <endif>" +

    "ORDER BY <sortColumn> IS NULL, <sortColumn> <sortOrder> " +
    "limit :limit offset :offset"
  )
  @UseStringTemplateEngine
  List<ImpalaQueryEntity> search(
    @Bind("startTime") Long startTime, @Bind("endTime") Long endTime,
    @Define("checkCurrentUser") Boolean checkCurrentUser, @Bind("currentUser") String currentUser,

    @Define("checkText") Boolean checkText, @Bind("text") String text, @Bind("queryText") String queryText,

    @Define("checkStatus") Boolean checkStatus,
      @BindList(value = "statuses", onEmpty = EmptyHandling.NULL_STRING) List<Object> statuses,
    @Define("checkQueryType") Boolean checkQueryType,
      @BindList(value = "queryTypes", onEmpty = EmptyHandling.NULL_STRING) List<Object> queryTypes,
    @Define("checkUserNames") Boolean checkUserNames,
      @BindList(value = "userNames", onEmpty = EmptyHandling.NULL_STRING) List<Object> userNames,
    @Define("checkCoordinator") Boolean checkCoordinator,
      @BindList(value = "coordinators", onEmpty = EmptyHandling.NULL_STRING) List<Object> coordinators,

    @Define("sortColumn") String sortColumn, @Define("sortOrder") String sortOrder,
    @Bind("limit") Integer limit, @Bind("offset") Integer offset
  );

  @SqlQuery("select count(*) from impala_query " +
      "where start_time >= :startTime AND start_time \\<= :endTime " +
      "<if(checkCurrentUser)> AND user_name = :currentUser <endif> ")
  @UseStringTemplateEngine
  long getSearchSize(
    @Bind("startTime") Long startTime, @Bind("endTime") Long endTime,
    @Define("checkCurrentUser") boolean checkCurrentUser, @Bind("currentUser") String currentUser
  );

  @Override
  @SqlUpdate("insert into impala_query (query_id,query_text,status,query_type," +
      "start_time,end_time,duration,user_name,coordinator," +
      "cpu_time,rows_produced,peak_memory,hdfs_bytes_read,source,version) " +
      "values " +
      "(:queryId,:queryText,:status,:queryType,:startTime,:endTime,:duration," +
      ":userName,:coordinator,:cpuTime,:rowsProduced,:peakMemory,:hdfsBytesRead,cast(:source as jsonb),0)")
  @GetGeneratedKeys
  long insert(@BindBean ImpalaQueryEntity entity);

  @Override
  @SqlUpdate("update impala_query set query_id = :queryId, query_text = :queryText, " +
      "status = :status, query_type = :queryType, start_time = :startTime, end_time = :endTime, " +
      "duration = :duration, user_name = :userName, coordinator = :coordinator, cpu_time = :cpuTime, " +
      "rows_produced = :rowsProduced, peak_memory = :peakMemory, hdfs_bytes_read = :hdfsBytesRead, " +
      "source = cast(:source as jsonb), version = :version + 1 " +
      "where id = :id and version = :version" )
  int update(@BindBean ImpalaQueryEntity query);

  @Override
  @SqlUpdate("delete from impala_query where id = :id")
  int delete(@Bind("id") long id);

  @SqlUpdate("delete from impala_query where start_time < :startTime")
  int deleteOlder(@Bind("startTime") long startTime);

  @RegisterBeanMapper(FacetEntry.class)
  @SqlQuery("select <facetField> as key, count(<facetField>) as value from impala_query " +
      "where start_time >= :startTime AND start_time \\<= :endTime " +
      "<if(checkCurrentUser)> AND user_name = :currentUser <endif> " +
      "GROUP BY <facetField> " +
      "ORDER BY count(<facetField>) DESC LIMIT :facetsResultLimit")
  @UseStringTemplateEngine
  List<FacetEntry> getFacetValues(@Define("facetField") String facetField,
      @Bind("startTime") long startTime, @Bind("endTime") long endTime,
      @Define("checkCurrentUser") boolean checkCurrentUser, @Bind("currentUser") String currentUser,
      @Bind("facetsResultLimit") int facetsResultLimit);
}
