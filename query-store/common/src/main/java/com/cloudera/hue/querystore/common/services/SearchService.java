// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.services;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.function.Function;
import java.util.stream.Collectors;
import java.util.stream.IntStream;
import java.util.stream.Stream;

import javax.inject.Inject;
import javax.inject.Named;

import org.jdbi.v3.core.mapper.JoinRow;

import com.cloudera.hue.querystore.common.dto.DagDto;
import com.cloudera.hue.querystore.common.dto.FacetEntry;
import com.cloudera.hue.querystore.common.dto.FacetValue;
import com.cloudera.hue.querystore.common.dto.FieldInformation;
import com.cloudera.hue.querystore.common.dto.HiveQueryDto;
import com.cloudera.hue.querystore.common.dto.SearchRequest;
import com.cloudera.hue.querystore.common.entities.HiveQueryBasicInfo;
import com.cloudera.hue.querystore.common.entities.TezDagBasicInfo;
import com.cloudera.hue.querystore.common.repository.HiveQueryBasicInfoRepository;
import com.cloudera.hue.querystore.common.repository.PageData;
import com.cloudera.hue.querystore.common.repository.transaction.DASTransaction;
import com.cloudera.hue.querystore.common.util.Pair;
import com.cloudera.hue.querystore.generator.CountQueryGenerator;
import com.cloudera.hue.querystore.generator.FacetQueryGenerator;
import com.cloudera.hue.querystore.generator.NullHighlightQueryFunctionGenerator;
import com.cloudera.hue.querystore.generator.SearchQueryGenerator;
import com.cloudera.hue.querystore.orm.EntityField;
import com.cloudera.hue.querystore.parsers.FacetInputParser;
import com.cloudera.hue.querystore.parsers.FacetParseResult;
import com.cloudera.hue.querystore.parsers.QueryParseResult;
import com.cloudera.hue.querystore.parsers.RangeFacetInputParser;
import com.cloudera.hue.querystore.parsers.SearchQueryParser;
import com.cloudera.hue.querystore.parsers.SortInputParser;
import com.cloudera.hue.querystore.parsers.SortParseResult;
import com.cloudera.hue.querystore.parsers.TimeRangeInputParser;
import com.cloudera.hue.querystore.parsers.TimeRangeParseResult;
import com.google.common.collect.Lists;

import lombok.extern.slf4j.Slf4j;

/**
 * Service to perform the search
 */
@Slf4j
public class SearchService {
  private static final String RANGE_FACET_IDENTIFIER_TEXT = "range-facet";
  private static final String FACET_IDENTIFIER_TEXT = "facet";

  private static volatile List<FieldInformation> fieldsInformation = null;
  private static final String SORT_FRAGMENT = "ORDER BY %s NULLS LAST";

  private final SearchQueryParser basicParser;
  private final SortInputParser sortInputParser;
  private final FacetInputParser facetParser;
  private final RangeFacetInputParser rangeFacetParser;
  private final TimeRangeInputParser timeRangeInputParser;
  private final HiveQueryBasicInfoRepository repository;

  @Inject
  public SearchService(@Named("Basic") SearchQueryParser basicParser,
                       SortInputParser sortInputParser,
                       FacetInputParser facetParser,
                       RangeFacetInputParser rangeFacetParser,
                       TimeRangeInputParser timeRangeInputParser,
                       HiveQueryBasicInfoRepository repository) {
    this.basicParser = basicParser;
    this.sortInputParser = sortInputParser;
    this.facetParser = facetParser;
    this.rangeFacetParser = rangeFacetParser;
    this.timeRangeInputParser = timeRangeInputParser;
    this.repository = repository;
  }

  public PageData<HiveQueryDto> doBasicSearch(String queryText, String sortText, Integer offset,
      Integer limit, Long startTime, Long endTime, List<SearchRequest.Facet> facets,
      List<SearchRequest.RangeFacet> rangeFacets, String username) {

    int iOffset = SanitizeUtility.sanitizeOffset(offset);
    int iLimit = SanitizeUtility.sanitizeLimit(limit);
    String iQueryText = SanitizeUtility.sanitizeQuery(queryText);
    String iSortText = SanitizeUtility.sanitizeQuery(sortText);
    Long iEndTime = SanitizeUtility.sanitizeEndTime(startTime, endTime);
    Long iStartTime = SanitizeUtility.sanitizeStartTime(startTime, endTime);

    QueryParseResult parseResult = basicParser.parse(iQueryText);
    SortParseResult sortParseResult = sortInputParser.parse(iSortText);
    FacetParseResult facetParseResult = facetParser.parse(facets);
    FacetParseResult rangeFacetParseResult = rangeFacetParser.parse(rangeFacets);
    TimeRangeParseResult timeRangeParseResult = timeRangeInputParser.parse(new Pair<>(iStartTime, iEndTime));

    String sortFragment = sortParseResult.isSortingRequired()
        ? String.format(SORT_FRAGMENT, sortParseResult.getSortExpression()) : "";

  //TODO - highlightQueryFunction must be fully removed 
    final String highlightQueryFunction = new NullHighlightQueryFunctionGenerator()
        .generate(EntityField.dummyWithProjection("highlighted_query"));

    List<String> predicates = Lists.newArrayList(parseResult.getPredicate(), facetParseResult.getFacetExpression(),
        rangeFacetParseResult.getFacetExpression(), timeRangeParseResult.getTimeRangeExpression());

    if (username != null) {
      predicates.add(HiveQueryBasicInfo.TABLE_INFORMATION.getTablePrefix() + ".request_user = :username");
    }

    SearchQueryGenerator searchQueryGenerator = new SearchQueryGenerator(
        HiveQueryBasicInfo.TABLE_INFORMATION, TezDagBasicInfo.TABLE_INFORMATION, "offset", "limit",
        highlightQueryFunction, sortFragment, predicates);
    String finalSql = searchQueryGenerator.generate();

    CountQueryGenerator countQueryGenerator = new CountQueryGenerator(
        HiveQueryBasicInfo.TABLE_INFORMATION, TezDagBasicInfo.TABLE_INFORMATION, "query_count", predicates);
    String finalCountSql = countQueryGenerator.generate();

    Map<String, Object> parameterBindings = new HashMap<>();
    parameterBindings.putAll(parseResult.getParameterBindings());
    parameterBindings.putAll(facetParseResult.getParameterBindings());
    parameterBindings.putAll(rangeFacetParseResult.getParameterBindings());
    parameterBindings.putAll(timeRangeParseResult.getParameterBindings());
    if (username != null) {
      parameterBindings.put("username", username);
    }

    Map<String, Object> countParameterBindings = new HashMap<>(parameterBindings);

    parameterBindings.put("limit", iLimit);
    parameterBindings.put("offset", iOffset);

    log.debug("Final query: {}", finalSql);
    log.debug("Final count query: {}", finalCountSql);

    List<JoinRow> rows = repository.executeSearchQuery(finalSql, parameterBindings);
    List<HiveQueryDto> queries = new ArrayList<>(rows.size());
    Map<Long, HiveQueryDto> seenQueries = new HashMap<>(rows.size());
    for (JoinRow row : rows) {
      HiveQueryBasicInfo query = row.get(HiveQueryBasicInfo.class);
      TezDagBasicInfo dagInfo = row.get(TezDagBasicInfo.class);
      HiveQueryDto dto = seenQueries.get(query.getId());
      if (dto == null) {
        dto = new HiveQueryDto(query, null, new ArrayList<>());
        seenQueries.put(query.getId(), dto);
        queries.add(dto);
      }
      if (dagInfo != null && dagInfo.getId() != null) {
        dto.getDags().add(new DagDto(dagInfo, null, null));
      }
    }
    Long queryCount = repository.executeSearchCountQuery(finalCountSql, countParameterBindings);

    return new PageData<>(queries, iOffset, iLimit, queryCount);
  }

  @DASTransaction
  public Pair<List<FacetValue>, List<FacetValue>> getFacetValues(String queryText,
      Set<String> facetFields, Long startTime, Long endTime, String username) {
    String iQueryText = SanitizeUtility.sanitizeQuery(queryText);
    Long iEndTime = SanitizeUtility.sanitizeEndTime(startTime, endTime);
    Long iStartTime = SanitizeUtility.sanitizeStartTime(startTime, endTime);

    QueryParseResult parseResult = basicParser.parse(iQueryText);
    TimeRangeParseResult timeRangeParseResult = timeRangeInputParser.parse(new Pair<>(iStartTime, iEndTime));

    List<String> predicates = Lists.newArrayList(parseResult.getPredicate(),
        timeRangeParseResult.getTimeRangeExpression());
    if (username != null) {
      predicates.add(HiveQueryBasicInfo.TABLE_INFORMATION.getTablePrefix() + ".request_user = :username");
    }

    FacetQueryGenerator facetCountQuery = new FacetQueryGenerator(HiveQueryBasicInfo.TABLE_INFORMATION,
        TezDagBasicInfo.TABLE_INFORMATION, new HashSet<>(facetFields), predicates);
    String finalSql = facetCountQuery.generate();
    log.debug("Final facet query: {}", finalSql);

    Map<String, Object> parameterBindings = new HashMap<>();
    parameterBindings.putAll(parseResult.getParameterBindings());
    parameterBindings.putAll(timeRangeParseResult.getParameterBindings());
    parameterBindings.put("username", username);

    List<FacetEntry> entries = repository.executeFacetQuery(finalSql, parameterBindings);
    return extractFacetsFromEntries(entries);
  }

  private Pair<List<FacetValue>, List<FacetValue>> extractFacetsFromEntries(List<FacetEntry> entries) {
    ArrayList<FacetEntry> entriesArrayList = new ArrayList<>(entries);
    Stream<Integer> indexStream = IntStream.range(0, entries.size()).boxed().filter(i -> {
      FacetEntry facetEntry = entriesArrayList.get(i);
      return facetEntry.isFirst();
    });

    List<Integer> partitionIndexes = indexStream.collect(Collectors.toList());
    partitionIndexes.add(entries.size());

    List<List<FacetEntry>> subSets = IntStream.range(0, partitionIndexes.size() - 1)
        .mapToObj(i -> entriesArrayList.subList(partitionIndexes.get(i), partitionIndexes.get(i + 1)))
        .collect(Collectors.toList());

    List<FacetValue> facets = new ArrayList<>();
    List<FacetValue> rangeFacets = new ArrayList<>();

    for(List<FacetEntry> subSet : subSets) {
      FacetEntry topEntry = subSet.get(0);
      String facetKey = topEntry.getType().toLowerCase();
      List<FacetEntry> facetEntries = subSet.subList(1, subSet.size());
      if(facetKey.startsWith(RANGE_FACET_IDENTIFIER_TEXT)) {
        if (rangeFacetShouldBeAdded(facetEntries)) {
          rangeFacets.add(new FacetValue(topEntry.getKey(), facetEntries));
        }
      }

      if(facetKey.startsWith(FACET_IDENTIFIER_TEXT)) {
        facets.add(new FacetValue(topEntry.getKey(), facetEntries));
      }
    }
    return new Pair<>(facets, rangeFacets);
  }

  private boolean rangeFacetShouldBeAdded(List<FacetEntry> facetEntries) {
    if(facetEntries.size() != 2) return false;
    long nullValueEntryCount = facetEntries.stream().filter(x -> x.getValue() == null).count();
    return nullValueEntryCount == 0;
  }

  public static List<FieldInformation> getFieldsInformation() {
    if (fieldsInformation == null) {
      synchronized (SearchService.class) {
        Function<EntityField, FieldInformation> entityFieldConsumer = x -> new FieldInformation(
          x.getExternalFieldName(), x.getDisplayName(), x.isSearchable(), x.isSortable(), x.isFacetable(),
          x.isRangeFacetable());
        ArrayList<FieldInformation> fieldsInformation = new ArrayList<>();
        fieldsInformation.addAll(HiveQueryBasicInfo.TABLE_INFORMATION.getFields().stream()
          .filter(x -> !x.isExclude())
          .map(entityFieldConsumer)
          .collect(Collectors.toList()));
        fieldsInformation.addAll(TezDagBasicInfo.TABLE_INFORMATION.getFields().stream()
          .filter(x -> !x.isExclude())
          .map(entityFieldConsumer)
          .collect(Collectors.toList()));
        SearchService.fieldsInformation = fieldsInformation;
      }
    }
    return fieldsInformation;
  }
}
