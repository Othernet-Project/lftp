<%namespace name="forms" file="/ui/forms.tpl"/>
<%namespace name="ftp_settings_form" file="_ftp_settings_form.tpl"/>

${h.form('post', action=i18n_url('ftp:settings'), id="ftp-settings-form")}
    ${ftp_settings_form.body()}
</form>
<script type="text/template" id="ftpSettingsSaveError">
    <% 
    # Translators, error message when settings cannot be saved
    errors = [_('Settings could not be set due to application error.')] 
    %>
    ${forms.form_errors(errors)}
</script>
<script type="text/template" id="ftpSettingsSaveOK">
    <p class="o-form-message">${_('Settings were saved.')}</p>
</script>
