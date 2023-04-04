package com.cloudera.hue.querystore.common.dto;

import java.util.HashMap;
import java.util.List;

import com.cloudera.hue.querystore.common.entities.HiveQueryBasicInfo;
import com.cloudera.hue.querystore.common.entities.ImpalaQueryEntity;
import com.google.common.base.Strings;

import lombok.Getter;

@Getter
public class HiveSearchDetails {
  private String text;
  private String queryText;

  // facet fields
  public List<Object> statuses;
  public List<Object> queueNames;
  public List<Object> userIds;
  public List<Object> requestUsers;
  public List<Object> executionModes;
  public List<Object> usedCbo;

  public HiveSearchDetails(QuerySearchParams params) {
    String text = params.getText();

    if (!Strings.isNullOrEmpty(text)) {
      this.text = text;
      this.queryText = "%" + text + "%";
    }

    HashMap<String, List<Object>> facetMap = params.getFacetMap();

    this.statuses = facetMap.get(HiveQueryBasicInfo.Fields.status);
    this.queueNames = facetMap.get(HiveQueryBasicInfo.Fields.queueName);
    this.userIds = facetMap.get(HiveQueryBasicInfo.Fields.userId);
    this.requestUsers = facetMap.get(HiveQueryBasicInfo.Fields.requestUser);
    this.executionModes = facetMap.get(HiveQueryBasicInfo.Fields.executionMode);
    this.usedCbo = facetMap.get(HiveQueryBasicInfo.Fields.usedCbo);
  }
}
