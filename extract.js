/*
 * extract.js
 *
 * Adds a button to the NYTimes crossword page to extract the day's leaderboard data to JSON.
 */

// Identify the bar div to add the new button
buttonBar = document.getElementsByClassName("lbd-board__actions")[0]

// Create the blob URL for the JSON
json = Array.from(document.getElementsByClassName("lbd-score")).map(item =>
    ({
        name: item.childNodes[1].childNodes[0].data,
        time: item.childNodes[2].childNodes[0].data
    })
)
jsonBlob = new Blob([JSON.stringify(json)], {type: "application/json"})
jsonURL = URL.createObjectURL(jsonBlob)

// Create the new button
newNode = document.createElement("a")
newNode.className = "lbd-button white"
newNode.href = jsonURL
d = new Date()
newNode.download = "crossword_" + [d.getFullYear(), d.getMonth() + 1, d.getDay()].join('-') + ".json"
newNode.appendChild(document.createTextNode("Extract Data"))

// Append the new button
buttonBar.appendChild(newNode)


