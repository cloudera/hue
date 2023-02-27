package com.cloudera.hue.querystore.common.dto;

import java.util.HashMap;
import java.util.List;

import com.cloudera.hue.querystore.common.entities.ImpalaQueryEntity;
import com.google.common.base.Strings;

import lombok.Getter;

@Getter
public class ImpalaSearchDetails {
  private String text;
  private String queryText;

  private List<Object> statuses;
  private List<Object> queryTypes;

  private List<Object> userNames;
  private List<Object> coordinators;

  public ImpalaSearchDetails(QuerySearchParams params) {

    String text = params.getText();
    if(!Strings.isNullOrEmpty(text)) {
      this.text = text;
      this.queryText = "%" + text + "%";
    }

    HashMap<String, List<Object>> facetMap = params.getFacetMap();
    this.statuses = facetMap.get(ImpalaQueryEntity.Fields.status);
    this.queryTypes = facetMap.get(ImpalaQueryEntity.Fields.queryType);

    this.userNames = facetMap.get(ImpalaQueryEntity.Fields.userName);
    this.coordinators = facetMap.get(ImpalaQueryEntity.Fields.coordinator);
  }
}
