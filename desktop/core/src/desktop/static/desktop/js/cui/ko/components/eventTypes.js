// (c) Copyright 2016 Cloudera, Inc. All rights reserved.
/**
 * @module ko/components/eventTypes
 * @description A registry of component events.
 */
module.exports = {
  USER_FEEDBACK_FORM_SUBMIT: 'cloudera-ui.userFeedbackForm.submit',
  /**
   * Tells modalLoader.js to load a component into it's inner template.
   */
  SHOW_COMPONENT_MODAL: 'cloudera-ui.modalLoader.showModal',
  SHOW_COMPONENT_MESSAGE: 'cloudera-ui.messageLoader.showMessage',
  REMOVE_COMPONENT_MESSAGE: 'cloudera-ui.messageLoader.removeMessage'
};

