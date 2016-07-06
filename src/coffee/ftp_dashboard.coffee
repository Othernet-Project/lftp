((window, $, templates) ->

  section = $ '#dashboard-ftp'
  form = null
  url = null
  successMessage = templates.ftpSettingsSaveOK
  errorMessage = templates.ftpSettingsSaveError


  removeMessage = () ->
    (form.find '.o-form-message').slideUp () ->
      ($ this).remove()


  submitData = (data) ->
    res = $.post url, data
    res.done (data) ->
      form.append successMessage
      (form.parents '.o-collapsible-section').trigger 'remax'
      setTimeout removeMessage, 3000
    res.fail () ->
      form.append errorMessage


  initPlugin = () ->
    form = section.find '#ftp-settings-form'
    url = form.attr 'action'
    form.on 'submit', (e) ->
      e.preventDefault()
      data = form.serialize()
      submitData data


  section.on 'dashboard-plugin-loaded', initPlugin

) this, this.jQuery, this.templates
