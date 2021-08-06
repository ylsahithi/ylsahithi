// See https://github.com/dialogflow/dialogflow-fulfillment-nodejs
// for Dialogflow fulfillment library docs, samples, and to report issues
'use strict';
 
const functions = require('firebase-functions');
const {WebhookClient} = require('dialogflow-fulfillment');
const {Card, Suggestion} = require('dialogflow-fulfillment');
 
process.env.DEBUG = 'dialogflow:debug'; // enables lib debugging statements
 
exports.dialogflowFirebaseFulfillment = functions.https.onRequest((request, response) => {
  const agent = new WebhookClient({ request, response });
  console.log('Dialogflow Request headers: ' + JSON.stringify(request.headers));
  console.log('Dialogflow Request body: ' + JSON.stringify(request.body));
 
  function welcome(agent) {
    agent.add(`Welcome to travel booking ! Can you give me source destination and date of travel`);
  }
 
  function fallback(agent) {
    agent.add(`I didn't understand`);
    agent.add(`I'm sorry, can you try again?`);
  }
  
  function JourneydetailsHandler(agent) {
    const source = agent.parameters.source;
    const destination = agent.parameters.destination;
    const date = agent.parameters.date;
    if (source && destination && date) {
      	var date1 = new Date(date);
        var month = date1.getUTCMonth() + 1;
        var day = date1.getUTCDate();
      	var year = "2021";
        var update_date = new Date(month+"/"+day+"/"+year);
        var present_date = new Date();
        var diff_days = parseInt((update_date - present_date) / (1000 * 60 * 60 * 24));
        if(diff_days > 0) {
        agent.add(`There are 3 flights from Portland to NewYork JFK on ${date1} ${update_date}. 
                   flight with carrier ID - 870 direct flight costs about 500$, 
        		   Carrier ID - 987 is direct flight costs 430$,
                   Carrier ID 765 is not a direct flight costs 256$ which one do you want to choose?`);
        }
        else {
          agent.add(` invalid date for travel ${date1} ${update_date} `);
        }
    } else {
        agent.add(`From fulfillment: Something is missing`);
    }
}
  
  function GetuserflightchoiceHandler(agent) {
    const flight_number = agent.parameters.flight_number;
    if (flight_number != 870 && flight_number != 987 && flight_number != 765) {
        agent.add(`Looks like you have choosen incorrect flight number, please choose it from 870,987,765. `);
    } else {
        agent.add(` Your travel is booked, do you want to set a reminder about travel ?`);
    }
}
  
    function SettravelreminderHandler(agent) {
    const response_reminder = agent.parameters.responseforreminder;
    if (response_reminder != "Yes" && response_reminder != "Yeah") {
        agent.add(` Is there anything else i can help you with? `);
    } else {
        agent.add(` Your reminder is set for travel.`);
    }
}


  // // Uncomment and edit to make your own intent handler
  // // uncomment `intentMap.set('your intent name here', yourFunctionHandler);`
  // // below to get this function to be run when a Dialogflow intent is matched
  // function yourFunctionHandler(agent) {
  //   agent.add(`This message is from Dialogflow's Cloud Functions for Firebase editor!`);
  //   agent.add(new Card({
  //       title: `Title: this is a card title`,
  //       imageUrl: 'https://developers.google.com/actions/images/badges/XPM_BADGING_GoogleAssistant_VER.png',
  //       text: `This is the body text of a card.  You can even use line\n  breaks and emoji! 💁`,
  //       buttonText: 'This is a button',
  //       buttonUrl: 'https://assistant.google.com/'
  //     })
  //   );
  //   agent.add(new Suggestion(`Quick Reply`));
  //   agent.add(new Suggestion(`Suggestion`));
  //   agent.setContext({ name: 'weather', lifespan: 2, parameters: { city: 'Rome' }});
  // }

  // // Uncomment and edit to make your own Google Assistant intent handler
  // // uncomment `intentMap.set('your intent name here', googleAssistantHandler);`
  // // below to get this function to be run when a Dialogflow intent is matched
  // function googleAssistantHandler(agent) {
  //   let conv = agent.conv(); // Get Actions on Google library conv instance
  //   conv.ask('Hello from the Actions on Google client library!') // Use Actions on Google library
  //   agent.add(conv); // Add Actions on Google library responses to your agent's response
  // }
  // // See https://github.com/dialogflow/fulfillment-actions-library-nodejs
  // // for a complete Dialogflow fulfillment library Actions on Google client library v2 integration sample

  // Run the proper function handler based on the matched Dialogflow intent name
  let intentMap = new Map();
  intentMap.set('Default Welcome Intent', welcome);
  intentMap.set('Default Fallback Intent', fallback);
  intentMap.set('GetJourneyDetails', JourneydetailsHandler);
  intentMap.set('Getuserflightchoice', GetuserflightchoiceHandler);
  // intentMap.set('your intent name here', yourFunctionHandler);
  // intentMap.set('your intent name here', googleAssistantHandler);
  agent.handleRequest(intentMap);
});
