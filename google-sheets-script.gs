const sheetName = 'Sheet1'; // Replace with your sheet name if different

function doPost(e) {
  try {
    const doc = SpreadsheetApp.getActiveSpreadsheet();
    const sheet = doc.getSheetByName(sheetName);

    const headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
    const nextRow = sheet.getLastRow() + 1;

    const newRow = headers.map(function(header) {
      switch (header.trim()) {
        case 'First Name': return e.parameter.firstName || '';
        case 'Last Name': return e.parameter.lastName || '';
        case 'Email': return e.parameter.email || '';
        case 'Phone Number': return e.parameter.phoneNumber || '';
        case 'Date of Birth': return `${e.parameter.dobYear}-${e.parameter.dobMonth}-${e.parameter.dobDay}` || '';
        case 'Gender': return e.parameter.gender || '';
        case 'Location': return e.parameter.location || '';
        case 'Education Level': return e.parameter.educationLevel || '';
        case 'Employment Status': return e.parameter.employmentStatus || '';
        case 'LinkedIn URL': return e.parameter.linkedinUrl || '';
        case 'Entrepreneurial Experience (Years)': return e.parameter.entrepreneurialExperience || '';
        case 'Previous Startups': return e.parameter.previousStartups || '';
        case 'Current Startups/Projects': return e.parameter.currentStartups || '';
        case 'Type of Entrepreneurial Experience': return e.parameter.entrepreneurialExperienceType || '';
        case 'Previously held startup roles': return e.parameter.startupRoles || '';
        case 'Current Startup Stage': return e.parameter.startupStage || '';
        case 'Startup Project Name': return e.parameter.startupProjectName || '';
        case 'First Challenge': return e.parameter.firstChallenge || '';
        case 'Second Challenge': return e.parameter.secondChallenge || '';
        case 'Third Challenge': return e.parameter.thirdChallenge || '';
        default: return ''; // Handle unknown headers if any
      }
    });

    sheet.getRange(nextRow, 1, 1, newRow.length).setValues([newRow]);

    return ContentService
      .createTextOutput(JSON.stringify({ 'result': 'success', 'row': nextRow }))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (e) {
    return ContentService
      .createTextOutput(JSON.stringify({ 'result': 'error', 'error': e }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}
