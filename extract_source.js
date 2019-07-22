/*
 * extract.js
 *
 * Adds a button to the NYTimes crossword page to extract the day's leaderboard data to JSON.
 */

// Identify the bar div to add the new button
buttonBar = document.getElementsByClassName("lbd-board__actions")[0]

// Get a date string
d = new Date()
dateString = [d.getFullYear(), d.getMonth() + 1, d.getDate()].join('-') 

// Create the blob URL for the JSON
json = ({
        data: Array.from(document.getElementsByClassName("lbd-score")).map(item =>
            ({
                name: item.childNodes[1].childNodes[0].data,
                time: item.childNodes[2].childNodes[0].data
            })),
        date: dateString
    })

jsonBlob = new Blob([JSON.stringify(json)], {type: "application/json"})
jsonURL = URL.createObjectURL(jsonBlob)

// Create the new button
newNode = document.createElement("a")
newNode.className = "lbd-button white"
newNode.href = jsonURL
newNode.download = "crossword_" + dateString + ".json"
newNode.appendChild(document.createTextNode("Extract Data"))

// Append the new button
buttonBar.appendChild(newNode)

// initialize cron jobs
var cron = require('cron-scheduler')

// schedule to fetch score, 10pm on weekdays and 6pm weekends 
sched = ['55 5 * * 0', '55 9 * * 1', '55 9 * * 2', '55 9 * * 3', '55 9 * * 4', '55 9 * * 5', '55 5 * * 6']

for (i = 0; i < sched.length; i++) {
    cron({ on: sched[i] }, function () {
        window.location.reload(true); 
        console.log("downloading leaderboard")
        newNode.click();
    })
}
