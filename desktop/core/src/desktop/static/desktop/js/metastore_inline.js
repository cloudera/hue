function dropAndWatch(formElement) {
  $(formElement).find('input[name=start_time]').val(ko.mapping.toJSON(new Date().getTime()));
  $(formElement).ajaxSubmit({
    dataType: 'json',
    success: function(resp) {
      if (resp.history_uuid) {
        huePubSub.publish('notebook.task.submitted', resp);
        huePubSub.publish('metastore.clear.selection');
      } else if (resp && resp.message) {
        huePubSub.publish('hue.global.error', {message: resp.message});
      }
      $("#dropTable").modal('hide');
      $("#dropSingleTable").modal('hide');
      $("#dropDatabase").modal('hide');
      $("#dropPartition").modal('hide');
    },
    error: function (xhr) {
      huePubSub.publish('hue.global.error', {message: xhr.responseText});
    }
  });
}

function browsePartitionFolder(url) {
  $.get(url, {
    format: "json"
  },function(resp) {
    if (resp.uri_path) {
      huePubSub.publish('open.link', resp.uri_path);
    } else if (resp.message) {
      huePubSub.publish('hue.global.error', {message: resp.message});
    }
  }).fail(function (xhr) {
    huePubSub.publish('hue.global.error', {message: xhr.responseText});
  });
}

function queryAndWatchUrl(url, sourceType, namespaceId, compute) {
  $.post(url, {
    format: "json",
    sourceType: sourceType,
    namespace: namespaceId,
    cluster: compute
  },function(resp) {
    if (resp.history_uuid) {
      huePubSub.publish('open.editor.query', resp);
    } else if (resp.message) {
      huePubSub.publish('hue.global.error', {message: resp.message});
    }
  }).fail(function (xhr) {
    huePubSub.publish('hue.global.error', {message: xhr.responseText});
  });
}

function queryAndWatch(catalogEntry) {
  queryAndWatchUrl('/notebook/browse/' + catalogEntry.path.join('/') + '/', catalogEntry.getConnector().id,
          catalogEntry.namespace && catalogEntry.namespace.id, catalogEntry.compute)
}