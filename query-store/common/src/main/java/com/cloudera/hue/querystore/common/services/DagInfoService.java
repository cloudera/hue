// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.querystore.common.services;

import java.util.ArrayList;
import java.util.Collection;
import java.util.Optional;

import javax.inject.Inject;
import javax.inject.Provider;

import com.cloudera.hue.querystore.common.dto.DagDto;
import com.cloudera.hue.querystore.common.entities.TezAppInfo;
import com.cloudera.hue.querystore.common.entities.TezDagBasicInfo;
import com.cloudera.hue.querystore.common.entities.TezDagExtendedInfo;
import com.cloudera.hue.querystore.common.repository.TezAppInfoRepository;
import com.cloudera.hue.querystore.common.repository.TezDagBasicInfoRepository;
import com.cloudera.hue.querystore.common.repository.TezDagExtendedInfoRepository;
import com.fasterxml.jackson.databind.node.ObjectNode;

/**
 * Service to fetch the Dag Information
 */
public class DagInfoService {
  private final Provider<TezDagBasicInfoRepository> dagInfoRepo;
  private final Provider<TezDagExtendedInfoRepository> dagDetailsRepo;
  private final Provider<TezAppInfoRepository> tezAppInfoRepo;

  @Inject
  public DagInfoService(Provider<TezDagBasicInfoRepository> dagInfoRepo, Provider<TezDagExtendedInfoRepository> dagDetailsRepo,
      Provider<TezAppInfoRepository> tezAppInfoRepo) {
    this.dagInfoRepo = dagInfoRepo;
    this.dagDetailsRepo = dagDetailsRepo;
    this.tezAppInfoRepo = tezAppInfoRepo;
  }

  public Optional<TezDagBasicInfo> findOne(Long id) {
    return dagInfoRepo.get().findOne(id);
  }

  public Collection<DagDto> getAllDagDetails(Long hiveQueryId, boolean extended) {
    TezDagBasicInfoRepository dagRepo = dagInfoRepo.get();
    TezDagExtendedInfoRepository ddRepo = dagDetailsRepo.get();
    TezAppInfoRepository taRepo = tezAppInfoRepo.get();

    ArrayList<DagDto> dags = new ArrayList<>();
    for (TezDagBasicInfo info : dagRepo.getByHiveQueryTableId(hiveQueryId)) {
      TezDagExtendedInfo detail = null;
      ObjectNode config = null;
      if (extended) {
        Optional<TezDagExtendedInfo> dagDetails = ddRepo.findByDagId(info.getDagId());
        if (dagDetails.isPresent()) {
          detail = dagDetails.get();
        }
        Optional<TezAppInfo> appInfo = taRepo.findByDagInfoId(info.getId());
        if (appInfo.isPresent()) {
          config = appInfo.get().getConfig();
        }
      }
      dags.add(new DagDto(info, detail, config));
    }
    return dags;
  }
}
