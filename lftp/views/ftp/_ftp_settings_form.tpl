<%namespace name="forms" file="/ui/forms.tpl"/>
<p class="o-field">
    <input type="checkbox" id="ftp_enabled" name="ftp_enabled" value="ftp_enabled" ${'checked' if status else ''}>
    <label for="ftp_enabled" class="o-field-label o-field-label-inline">Enable FTP</label>
    <span class="o-field-help-message">Allow access to downloaded files through an anonymous read-only FTP server on port 21</span>
</p>
<p>
    <button type="submit" class="primary"><span class="icon"></span> ${_('Save')}</button>
</p>
