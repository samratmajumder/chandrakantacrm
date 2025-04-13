I want to build a simple web application for a store to provide price estimates to clients and then save the estimate data on the backend database. For auth use similar auth provider with a google based login.

The user journey will be: Authenticate and login (First time any user with authenticate google credential can login. Subsequent users will need to be added in Allowed users by their gmail id)

Customer estimate portal will be displayed which looks modern and stylish. Header will be the name and address of the store which can be configured via a markdown file. The first page will be a dashboard which will show how many estimates have been generated previous day, current month and current year. It will also show how many customers in database and how many unique Products. A graph showing enquiry/estimate trends of the last 4 days would also be nice

Customer entity will have Name, address and Mobile number

Estimate entity will have Serial, Item code, size, picture of the item, area required, quantity, rate and amount. Amount is of type float, Estimate date, time and Quotation number (This will be auto generated or even entered manually while creating estimate. If being entered manually it will check if the Quotation no is duplicate and warn the user. This is the primary key)

One Customer entity can have multiple estimates

There is a page for Customer search which can search for customer on the basis of name, date or mobile number. It will show all possible matches of estimates with all the details.

There is a page to create a new estimate: The attached image shows the structure of the new estimate page. User can start entering Mobile number and it will show matching customers in dropdown and the correct customer can be chosen. For the actual estimate section it will offer an excel like table structure with the provided columns and rows. By default there should be 5 rows with the option of adding more rows S.no in each row is auto generated. Size is text box. Item Code is a text box but whatever it will try to provide autocomplete suggestions from the items entity table. if none of the suggested items are chosen then the app will let the user type the full item code and when the estimate is saved it will also save the Code, picture and rate value in items table.

Even if item picture and rate is pre-populated from the db, the user can still overwrite the values in estimate page and on saving the estimate it will update items table as well

If it's a new item code then one has to upload a picture by clicking on the picture cell and the same will be visible as thumbnail

All amounts will be calculated as Qty * Rate. In qty give a drop down for Box or Piece. For every item added update the Total Amount

There should be a save option which would save estimate and all new items to backend db. After save a Printable layout is displayed with Print option to print the estimate.

We discussed about customer search which displays all the estimates for a customer. If the user opens an estimate it will display the estimate in print preview format with all the data pre-populated. Please note estimate should contain the original rate with which the estimate was created. Even if the rate for an item is changed, it should not change in the estimate

Build a rich and modern html5 web application, utilizing vanilla javascript with backend built with python flask. For database use sqlite3. 