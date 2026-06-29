// Google Apps Script — Wedding RSVP to Google Sheets
// Instructions:
// 1. Go to https://script.google.com
// 2. Create new project
// 3. Paste this entire code (replace default code)
// 4. Click "Deploy" → "New deployment"
// 5. Select "Web app" → Execute as: "Me", Who has access: "Anyone"
// 6. Click "Deploy" and copy the URL
// 7. Send the URL to me — I'll wire it into the wedding site

function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    
    // Get or create the spreadsheet
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    let sheet = ss.getSheetByName('RSVPs');
    
    if (!sheet) {
      sheet = ss.insertSheet('RSVPs');
      // Add headers
      sheet.appendRow(['Timestamp', 'Name', 'Email', 'Phone', 'Guests', 'Attendance', 'Notes']);
      // Format headers
      sheet.getRange(1, 1, 1, 7).setFontWeight('bold').setBackground('#5B1A2E').setFontColor('white');
      sheet.setColumnWidths(1, 7, 150);
    }
    
    // Add the RSVP data
    sheet.appendRow([
      data.timestamp || new Date().toISOString(),
      data.name || '',
      data.email || '',
      data.phone || '',
      data.guests || '1',
      data.attendance === 'yes' ? '✅ Accepts' : '❌ Declines',
      data.notes || ''
    ]);
    
    // Auto-resize columns
    sheet.autoResizeColumns(1, 7);
    
    return ContentService
      .createTextOutput(JSON.stringify({ status: 'success' }))
      .setMimeType(ContentService.MimeType.JSON);
      
  } catch (error) {
    return ContentService
      .createTextOutput(JSON.stringify({ status: 'error', message: error.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function doGet(e) {
  // Optional: view RSVP count via GET request
  try {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sheet = ss.getSheetByName('RSVPs');
    if (!sheet) {
      return ContentService
        .createTextOutput(JSON.stringify({ total: 0, accepts: 0, declines: 0 }))
        .setMimeType(ContentService.MimeType.JSON);
    }
    
    const data = sheet.getDataRange().getValues();
    const rsvps = data.slice(1); // skip header
    const accepts = rsvps.filter(r => r[5] && r[5].includes('Accepts')).length;
    const declines = rsvps.filter(r => r[5] && r[5].includes('Declines')).length;
    const totalGuests = rsvps.reduce((sum, r) => sum + (parseInt(r[4]) || 1), 0);
    
    return ContentService
      .createTextOutput(JSON.stringify({ 
        total: rsvps.length, 
        accepts: accepts, 
        declines: declines,
        totalGuests: totalGuests
      }))
      .setMimeType(ContentService.MimeType.JSON);
      
  } catch (error) {
    return ContentService
      .createTextOutput(JSON.stringify({ status: 'error', message: error.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}
