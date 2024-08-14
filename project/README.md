# Gerald's Budget Tracker
#### Video Demo:  https://youtu.be/msmilRlVW2U

## Description:

### My CS50x Final Project is a budget tracker that helps you keep track of your monthly spending and allows for the analysis of your spending.

#### You can add a budget to a new month and then add your monthly spending to that month. You can edit each spending and the changes will be registered in the database. It will also automatically update your total spending for that month, your budget left for that month, and the grand total. You can also edit the budget for that month if you feel that your budget is not enough. If new spending for that month is more than the leftover budget, there will be an error message. This forces users to add a budget for that month.

#### By clicking on the "View Bar Chart" tab, you can see how your spendings vary across the month and this provides insights into your spending habits. Through this, it can also highlight if there is an increase or decrease in spending in certain months. This tool can be used to make better spending choices.

#### By clicking on the "View Pie Chart" tab, you can see your spending breakdown for a particular month. This can be especially useful in helping users identify areas in which they should cut spending.

#### All in all, this web app is a tool for users to track their spending and prevent overspending by only spending within their budget.

## Explanation of what each file does:

#### app.py: It is the Python code in which my flask runs. I have imported modules such as datetime, which is used to convert integers representing months and years into the form of month name and year, calendar, which is used to convert integers representing months into the month name form, and random, which is used to generate integers between 0 to 255 to be used for the generation of RGB code.

#### helpers.py: It contains functions such as sgd which converts float into SGD currency format and contains the function to make sure users are logged in before they can access some other functions in app.py

#### layout.html: Layout on which other HTML templates are built on. Contains the HTML of the navigation bar, which collapses into a drop-down when the web app is viewed on smaller viewports and flash messages, which are used to flash messages when the user logs in or when a user adds a new spending breakdown or when the user changes an existing budget or adds a new budget. Also contains javascript to detect error messages from other HTML so that whenever I return render_template of another HTML with an error code, the web app will flash the error message and refuse to let the user proceed. This ensures that users give me the information my code needs to run. layout.html also contains javascript that allows my web app to be more responsive by changing the background color and border of the tabs in the navigation bar when they are clicked.

#### login.html: It is a page where users log in. It verifies users' usernames and passwords by checking with the SQLite3 database budget.db through TABLE users. It would prompt users for a username or password when users do not give either of those.

#### register.html: It is a page for users to register. It checks the database budget.db if username exists. It only allows users to register if username does not exist and stores the username and hashed password in budget.db under TABLE users. It would prompt users for a username or password or confirmation password when users do not give either of those. It will also check if the password and confirmation password match and if it does not match, it will prompt the user for the same password and confirmation password.

#### index.html: It allows users to select a month and year, and then display the spending breakdown of that month which is sorted by date. If no date is selected, it will prompt users for date input. If the month and year selected does not have a budget yet, it will redirect users to "/changebudget" for users to add a new budget to that month first. Breakdown in index is selected by passing the date into budget.db TABLE breakdown and displaying the output. It also allows users to add breakdown for that month, by redirecting to "/breakdown", edit breakdown for that month, by redirecting to "/editbreakdown", or delete breakdown for that month, by redirecting to "/deletebreakdown".

#### changebudget.html: It allows users to change the remaining budget for an existing month or add a budget for a new month. If the budget already exists for inputted date, it will UPDATE the TABLE budget. However, if the budget does not exist for that month, it will INSERT INTO the TABLE budget. It will prompt the user for date and budget if the users do not provide either of those.

#### addbreakdown.html: It allows users to add breakdown spending to a specific month. If selected month does not have a budget, it will prompt users to add a budget for that month first before allowing users to add breakdown. If inputted spending is more than the leftover budget, it will give an error that spending over budget. Users have to change the existing leftover budget first if they want to add the spending breakdown. It will prompt users to provide date, title and spending if users do not provide either of those. If nothing goes wrong, it will INSERT INTO TABLE breakdown in budget.db.

#### editbreakdown.html: It allows users to edit breakdown spending on an existing breakdown spending item. If inputted spending is more than the leftover budget, it will give an error that spending over budget. It will prompt users to provide title and spending if users do not provide either of those. If nothing goes wrong, it will UPDATE TABLE breakdown in budget.db

#### barchart.html: It allows users to select start and end date (only month and year) and through the barchart, display the spendings between the start and end date. I used chart.js for the API. It is done by passing every date (only month and year) between the start and end date into TABLE breakdown and SELECT the cost and adding the all breakdown costs for each month. The total breakdown costs for each month are then passed from app.py to barchart.html via JSON and through javascript, the barchart is updated with the new data from app.py. If end date is earlier than start date, it will prompt users that start date must be earlier than end date. It will prompt users for start and end dates if users do not provide either of those.

#### chart.html: It allows users to select a date (only month and year) and through the piechart, displays the spending breakdown of that month in the form of a piechart. It is done by passing the date (only month and year) into TABLE breakdown and SELECT the cost. If there are titles which are the same, it will add the breakdown costs for together and group the titles together in the piechart. The breakdown costs of each spending is then passed from app.py to piechart.html via JSON and through javascript, the piechart is updated with the new data from app.py. It will prompt users for a date if users do not provide a date.

#### redirect.html: It stores information and sends the information to index.html page so that users do not have to type the date again.

#### budget.db: It stores data such as users, breakdown and budget. TABLE users store the username and hashed password of users. TABLE breakdown stores the spending breakdown of users. TABLE budget stores the budget of each month of users.


