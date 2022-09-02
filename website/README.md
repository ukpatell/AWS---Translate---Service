<center>

# Translate - Service (Front End)</center>

NOTE  - Ensure you're in the correct path and all the necessary dependcies are installed correctly<br>

To start this application on http://localhost:3000/
```
$ npm start
```

<br><u>Structure of the components</u>

All of the components are located in the `components` folder and can be imported using the `index` file in that folder

|Component|Description|
|-|-|
|Controls|This component containts code for source & target language including all the function of switching etc.|
|Navbar|This component has all the necessary code for handing navigation & header|
|Text|This component/route contains the logic and UI for performating text translation|
|Document|This component/route contains required logic for performing document translation|
|NotFound|Any invalid path component|
---
<br>Work in progress for future additions
|Component|Description|
|-|-|
|Image|Image translations|
|Other|Providing other features such as Sentiment, Estimates etc|

`App.js` is the main component & defines the routes<br><br>
`secrets.json` is required in order to handle all the inboud/outbound API calls and will be generated once the `TranslateServiceStack` is ran from CDK deployment<br><br>

