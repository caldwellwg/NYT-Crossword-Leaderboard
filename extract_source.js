/*
 * extract.js
 *
 * Adds a button to the NYTimes crossword page to extract the day's leaderboard data to JSON.
 */


// initialize cron jobs
var cron = require('cron-scheduler')

// schedule to fetch score, 10pm on weekdays and 6pm weekends 
sched = ['55 16 * * 0', '55 20 * * 1', '55 20 * * 2', '55 20 * * 3', '55 20 * * 4', '55 20 * * 5', '55 16 * * 6']

for (i = 0; i < sched.length; i++) {
    cron({ on: sched[i] }, function () {
        window.location.reload(true); 

        // Identify the bar div to add the new button
        buttonBar = document.getElementsByClassName("lbd-board__actions")[0]

        // Get a date string
        d = new Date()
        dateString = [d.getFullYear(),
                      ("0" + (d.getMonth() + 1)).slice(-2),
                      ("0" + d.getDate()).slice(-2)].join('-') 
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

        newNode = document.createElement("a")
        newNode.className = "lbd-button white"
        newNode.href = jsonURL
        newNode.download = "crossword_" + dateString + ".json"
        newNode.appendChild(document.createTextNode("Extract Data"))

        // Append the new button
        buttonBar.appendChild(newNode)

        // Create the new button
        newNode.click();
    })
}
