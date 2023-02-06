// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.repository;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Optional;
import java.util.Set;

import org.junit.Assert;
import org.junit.Before;
import org.junit.Test;
import org.mockito.MockitoAnnotations;

import com.cloudera.hue.querystore.common.AppAuthentication;
import com.cloudera.hue.querystore.common.dao.HiveQueryBasicInfoDao;
import com.cloudera.hue.querystore.common.dto.FacetEntry;
import com.cloudera.hue.querystore.common.dto.FacetValue;
import com.cloudera.hue.querystore.common.repository.HiveQueryBasicInfoRepository;

public class HiveQueryBasicInfoRepositoryTest {
  private HiveQueryBasicInfoRepository hiveQueryService;
  private HiveQueryBasicInfoDao hiveQueryBasicInfoDao;
  private List<String> facetFields = Arrays.asList("tables_read", "tables_written");
  private final String UNKNOWN_FACET_FIELD = "unknown_facet_field";

  private Set<String> facetFieldSets;
  private Long startTime;
  private Long endTime;
  private String requestUser;
  private int facetsResultLimit;

  @Before
  public void setup() throws Exception { 
    MockitoAnnotations.initMocks(this);
    hiveQueryBasicInfoDao = mock(HiveQueryBasicInfoDao.class);
    hiveQueryService = new HiveQueryBasicInfoRepository(hiveQueryBasicInfoDao);

    facetFieldSets = new HashSet<>(facetFields);
    startTime = 1672311006606L;
    endTime = 1672915806606L;
    requestUser = "admin";
    boolean userCheck = false;
    facetsResultLimit = 2;

    when(hiveQueryBasicInfoDao.getFacetValues(UNKNOWN_FACET_FIELD, startTime, endTime, requestUser, userCheck, facetsResultLimit)).thenReturn(Collections.emptyList());
    when(hiveQueryBasicInfoDao.getFacetValues("tables_read", startTime, endTime, requestUser, userCheck, facetsResultLimit)).thenReturn(getFacetValuesForTablesRead());
    when(hiveQueryBasicInfoDao.getFacetValues("tables_written", startTime, endTime, requestUser, userCheck, facetsResultLimit)).thenReturn(getFacetValuesForTablesWritten());
    when(hiveQueryBasicInfoDao.getFacetValues("used_cbo", startTime, endTime, requestUser, userCheck, facetsResultLimit)).thenReturn(getFacetValuesForUsedCBO());

    // checking for the user-role USER, passing the userCheck as "true"
    when(hiveQueryBasicInfoDao.getFacetValues("user_id", startTime, endTime, requestUser, !userCheck, facetsResultLimit)).thenReturn(getFacetValuesForUserId());
  }

  @Test
  public void testMultipleFacetResults() {
    List<String> facetList = Arrays.asList("tables_read", "tables_written", "used_cbo");
    facetFieldSets = new HashSet<>(facetList);
    Optional<List<FacetValue>> facetValueList = hiveQueryService.getFacetValues(facetFieldSets, startTime, endTime, requestUser, AppAuthentication.Role.ADMIN, facetsResultLimit);
    List<FacetValue> facetValues = facetValueList.get();

    Assert.assertTrue(facetValueList.isPresent());
    Assert.assertEquals(facetValues.size(), 3);

    Assert.assertTrue(facetList.contains(facetValues.get(0).getFacetField()));
    Assert.assertTrue(facetList.contains(facetValues.get(1).getFacetField()));
    Assert.assertTrue(facetList.contains(facetValues.get(2).getFacetField()));
  }

  @Test
  public void testInvalidFacetName() {
    facetFieldSets = new HashSet<>(Arrays.asList(UNKNOWN_FACET_FIELD));
    Optional<List<FacetValue>> facetValueList = hiveQueryService.getFacetValues(facetFieldSets, startTime, endTime, requestUser, AppAuthentication.Role.ADMIN, facetsResultLimit);

    Assert.assertTrue(facetValueList.isPresent());
    Assert.assertEquals(facetValueList.get().size(), 1);
  }

  @Test
  public void testFewInvalidAndFewValidFacetNames() {
    List<String> facetList = Arrays.asList("tables_read", "tables_written", UNKNOWN_FACET_FIELD);

    facetFieldSets = new HashSet<>(facetList);
    Optional<List<FacetValue>> facetValueList = hiveQueryService.getFacetValues(facetFieldSets, startTime, endTime, requestUser, AppAuthentication.Role.ADMIN, facetsResultLimit);
    List<FacetValue> facetValues = facetValueList.get();

    Assert.assertTrue(facetValueList.isPresent());
    Assert.assertEquals(facetValues.size(), 3);

    Assert.assertTrue(facetList.contains(facetValues.get(0).getFacetField()));
    Assert.assertTrue(facetList.contains(facetValues.get(1).getFacetField()));
  }

  @Test
  public void testUserRoleAsUser() {
    facetFieldSets = new HashSet<>(Arrays.asList(UNKNOWN_FACET_FIELD));
    Optional<List<FacetValue>> facetValueList = hiveQueryService.getFacetValues(facetFieldSets, startTime, endTime, requestUser, AppAuthentication.Role.USER, facetsResultLimit);

    Assert.assertTrue(facetValueList.isPresent());
    Assert.assertEquals(facetValueList.get().size(), 1);
  }

  private List<FacetEntry> getFacetValuesForTablesRead(){
    List<FacetEntry> facetEntries = new ArrayList<FacetEntry>();
    FacetEntry facetEntry1 = new FacetEntry();
    facetEntry1.setKey("[{\"table\":\"_dummy_table\",\"database\":\"_dummy_database\"}]");
    facetEntry1.setValue(6L);

    FacetEntry facetEntry2 = new FacetEntry();
    facetEntry2.setKey("[]");
    facetEntry2.setValue(3L);

    facetEntries.add(facetEntry1);
    facetEntries.add(facetEntry2);
    return facetEntries;
  }

  private List<FacetEntry> getFacetValuesForTablesWritten(){
    List<FacetEntry> facetEntries = new ArrayList<FacetEntry>();
    FacetEntry facetEntry1 = new FacetEntry();
    facetEntry1.setKey("[]");
    facetEntry1.setValue(5L);

    FacetEntry facetEntry2 = new FacetEntry();
    facetEntry2.setKey("[{\\\"table\\\": \\\"sample_08\\\", \\\"database\\\": \\\"default\\\"}]");
    facetEntry2.setValue(2L);

    FacetEntry facetEntry3 = new FacetEntry();
    facetEntry3.setKey("[{\\\"table\\\": \\\"sample_07\\\", \\\"database\\\": \\\"default\\\"}]");
    facetEntry3.setValue(2L);

    FacetEntry facetEntry4 = new FacetEntry();
    facetEntry4.setKey("[{\\\"table\\\": \\\"web_logs\\\", \\\"database\\\": \\\"default\\\"}]");
    facetEntry4.setValue(1L);

    facetEntries.add(facetEntry1);
    facetEntries.add(facetEntry2);
    facetEntries.add(facetEntry3);
    facetEntries.add(facetEntry4);
    return facetEntries;
  }

  private List<FacetEntry> getFacetValuesForUsedCBO(){
    List<FacetEntry> facetEntries = new ArrayList<FacetEntry>();
    FacetEntry facetEntry1 = new FacetEntry();
    facetEntry1.setKey("t");
    facetEntry1.setValue(7L);

    FacetEntry facetEntry2 = new FacetEntry();
    facetEntry2.setKey("f");
    facetEntry2.setValue(3L);

    facetEntries.add(facetEntry1);
    facetEntries.add(facetEntry2);
    return facetEntries;
  }

  private List<FacetEntry> getFacetValuesForUserId(){
    List<FacetEntry> facetEntries = new ArrayList<FacetEntry>();
    FacetEntry facetEntry1 = new FacetEntry();
    facetEntry1.setKey("hive");
    facetEntry1.setValue(9L);

    facetEntries.add(facetEntry1);
    return facetEntries;
  }
}