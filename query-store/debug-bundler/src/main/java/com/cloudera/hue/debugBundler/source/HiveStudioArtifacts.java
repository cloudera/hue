// (c) Copyright 2020-2021 Cloudera, Inc. All rights reserved.
package com.cloudera.hue.debugBundler.source;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Optional;

import com.cloudera.hue.debugBundler.framework.Artifact;
import com.cloudera.hue.debugBundler.framework.ArtifactDownloadException;
import com.cloudera.hue.debugBundler.framework.ArtifactSource;
import com.cloudera.hue.debugBundler.framework.Params;
import com.cloudera.hue.debugBundler.framework.Params.DagParams;
import com.cloudera.hue.debugBundler.framework.ZipStream;
import com.cloudera.hue.querystore.common.dto.DagDto;
import com.cloudera.hue.querystore.common.entities.HiveQueryBasicInfo;
import com.cloudera.hue.querystore.common.entities.HiveQueryExtendedInfo;
import com.cloudera.hue.querystore.common.entities.TezAppInfo;
import com.cloudera.hue.querystore.common.entities.TezDagBasicInfo;
import com.cloudera.hue.querystore.common.entities.TezDagExtendedInfo;
import com.cloudera.hue.querystore.common.entities.VertexInfo;
import com.cloudera.hue.querystore.common.repository.HiveQueryBasicInfoRepository;
import com.cloudera.hue.querystore.common.repository.HiveQueryExtendedInfoRepository;
import com.cloudera.hue.querystore.common.repository.TezAppInfoRepository;
import com.cloudera.hue.querystore.common.repository.TezDagBasicInfoRepository;
import com.cloudera.hue.querystore.common.repository.TezDagExtendedInfoRepository;
import com.cloudera.hue.querystore.common.repository.VertexInfoRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.inject.Inject;

public class HiveStudioArtifacts implements ArtifactSource {

  private static final String FILE_EXT = "json";

  private final HiveQueryBasicInfoRepository hiveQueryBasicRepo;
  private final HiveQueryExtendedInfoRepository hiveQueryExtRepo;
  private final TezDagBasicInfoRepository dagBasicRepo;
  private final TezDagExtendedInfoRepository dagExtRepo;
  private final TezAppInfoRepository tezAppRepo;
  private final VertexInfoRepository vertexInfoRepo;
  private final ObjectMapper objectMapper;

  @Inject
  public HiveStudioArtifacts(HiveQueryBasicInfoRepository hiveQueryBasicRepo,
      HiveQueryExtendedInfoRepository hiveQueryExtRepo,
      TezDagBasicInfoRepository dagBasicRepo, TezDagExtendedInfoRepository dagExtRepo, TezAppInfoRepository tezAppRepo,
      VertexInfoRepository vertexInfoRepo, ObjectMapper objectMapper) {
    this.hiveQueryBasicRepo = hiveQueryBasicRepo;
    this.hiveQueryExtRepo = hiveQueryExtRepo;
    this.dagBasicRepo = dagBasicRepo;
    this.dagExtRepo = dagExtRepo;
    this.tezAppRepo = tezAppRepo;
    this.vertexInfoRepo = vertexInfoRepo;
    this.objectMapper = objectMapper;
  }

  @Override
  public List<Artifact> getArtifacts(Params params) {
    String queryId = params.getHiveQueryId();

    HiveQueryBasicInfo query = hiveQueryBasicRepo.findByHiveQueryId(queryId).get();
    Collection<TezDagBasicInfo> dags = dagBasicRepo.getByHiveQueryTableId(query.getId());
    // Collection<DagDto> dagDetails = dagBasicRepo.getAllDagDetails(query.get().getId(), true);

    List<Artifact> artifacts = new ArrayList<>(1 + dags.size() * 2);

    artifacts.add(new Artifact() {
      @Override
      public String getName() {
        return "QUERY." + FILE_EXT;
      }

      @Override
      public Object getData() throws ArtifactDownloadException {
        try {
          HiveQueryExtendedInfo queryDetails = hiveQueryExtRepo.findByHiveQueryTableId(query.getId()).get();
          HashMap<String, Object> data = new HashMap<String, Object>();
          data.put("query", query);
          data.put("queryDetails", queryDetails);
          return data;
      } catch (Exception e) {
          throw new ArtifactDownloadException("Error trying to fetch query details.", e);
        }
      }

      @Override
      public Object getContext() {
        return query.getExecutionMode();
      }
    });

    int i = 0;
    for (TezDagBasicInfo dagInfo : dags) {
      // DagInfo dagInfo = info.getDagInfo();
      DagParams tezInfo = dagInfo == null
          ? new DagParams(i, null, null)
          : new DagParams(i, dagInfo.getDagId(), dagInfo.getApplicationId());
      i++;
      DagDto dagDto = new DagDto();
      dagDto.setDagInfo(dagInfo);
      Optional<TezDagExtendedInfo> extInfo = dagExtRepo.findByDagId(dagInfo.getDagId());
      Optional<TezAppInfo> appInfo = tezAppRepo.findByDagInfoId(dagInfo.getId());
      if (extInfo.isPresent()) {
        dagDto.setDagDetails(extInfo.get());
      }
      if (appInfo.isPresent()) {
        dagDto.setConfig(appInfo.get().getConfig());
      }
      artifacts.add(new Artifact() {
        @Override
        public String getName() {
          return tezInfo.getDir("QP/DAG." + FILE_EXT);
        }

        @Override
        public Object getData() throws ArtifactDownloadException {
          try {
            HashMap<String, Object> data = new HashMap<String, Object>();
            data.put("dag", dagDto);
            return data;
          } catch (Exception e) {
            throw new ArtifactDownloadException("Error trying to fetch dag details.", e);
          }
        }

        @Override
        public Object getContext() {
          return tezInfo;
        }
      });

      artifacts.add(new Artifact() {
        @Override
        public String getName() {
          return tezInfo.getDir("QP/VERTEX." + FILE_EXT);
        }

        @Override
        public Object getData() throws ArtifactDownloadException {
          try {
            HashMap<String, Object> data = new HashMap<String, Object>();
            Collection<VertexInfo> vertexInfos = vertexInfoRepo.findAllByDagId(dagInfo.getDagId());
            data.put("vertices", vertexInfos);
            return data;
          } catch (Exception e) {
            throw new ArtifactDownloadException("Error trying to fetch vertices.", e);
          }
        }

        @Override
        public Object getContext() {
          return null;
        }
      });
    }

    return artifacts;
  }

  @Override
  public void process(Params params, Artifact artifact, ZipStream zipStream) throws ArtifactDownloadException {
    try {
      updateParams(params, artifact);

      @SuppressWarnings("unchecked")
      HashMap<String, Object> data = (HashMap<String, Object>)artifact.getData();
      zipStream.writeFile(artifact.getName(), objectMapper.writeValueAsBytes(data));
    } catch (IOException e) {
      throw new ArtifactDownloadException(e);
    }
  }

  public void updateParams(Params params, Artifact artifact) throws ArtifactDownloadException {
    Object context = artifact.getContext();
    if (context instanceof DagParams) {
      params.getDagParams().add((DagParams)context);
    } else if (context instanceof String) {
      params.setAppType((String)context);
    }
  }

  @Override
  public boolean hasRequiredParams(Params params) {
    return params.getHiveQueryId() != null;
  }
}
