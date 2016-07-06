((window, $, templates) ->

  section = $ '#dashboard-ftp'
  successMessageId = '#ftpSettingsSaveOK'
  errorMessageId = '#ftpSettingsSaveError'
  successMessage = null
  errorMessage = null
  form = null
  url = null


  removeMessage = () ->
    (form.find '.o-form-message').slideUp () ->
      ($ this).remove()


  submitData = (data) ->
    res = $.post url, data
    res.done (data) ->
      form.append successMessage
      section.trigger 'remax'
      setTimeout removeMessage, 3000
    res.fail () ->
      form.append errorMessage
      section.trigger 'remax'


  initPlugin = () ->
    $(successMessageId).loadTemplate()
    $(errorMessageId).loadTemplate()
    successMessage = templates.ftpSettingsSaveOK
    errorMessage = templates.ftpSettingsSaveError
    form = section.find '#ftp-settings-form'
    url = form.attr 'action'
    form.on 'submit', (e) ->
      e.preventDefault()
      data = form.serialize()
      submitData data


  section.on 'dashboard-plugin-loaded', initPlugin

) this, this.jQuery, this.templates
