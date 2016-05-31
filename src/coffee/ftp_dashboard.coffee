((window, $, templates) ->

  form = $ '#ftp-settings-form'
  url = form.attr 'action'
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


  form.on 'submit', (e) ->
    e.preventDefault()
    data = form.serialize()
    submitData data

) this, this.jQuery, this.templates
