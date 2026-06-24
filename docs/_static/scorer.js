// SPDX-License-Identifier: MIT

"use strict";

let queryParts = undefined;

function __getQuery() {
    const params = new URLSearchParams(window.location.search);
    const query = params.get('q');
    queryParts = query ? query.split(/\s+/g).map((s) => s.toLowerCase()) : null;
}

Scorer = {
    // Implement the following function to further tweak the score for each result
    // The function takes a result array [docname, title, anchor, descr, score, filename]
    // and returns the new score.
    score: (result) => {
        const [docname, title, anchor, descr, score, filename, kind] = result;

        if (queryParts === undefined) __getQuery();
        if (queryParts === null) return score;

        // For object name matches where the last dotted part exactly matches the query,
        // prioritize shorter (by parts) object names over longer ones, given otherwise same score.
        // (this then results in e.g. `disnake.Intents` appearing before `disnake.Client.intents` or
        // `disnake.ext.commands.Bot.intents`, which would all have the same score)
        if (kind === "object") {
            const parts = title.split(".");
            if (queryParts.includes(parts.slice(-1)[0].toLowerCase())) {
                return score + (1 - parts.length * 0.05);
            }
        }

        return score;
    },

    // query matches the full name of an object
    objNameMatch: 11,
    // or matches in the last dotted part of the object name
    objPartialMatch: 6,
    // Additive scores depending on the priority of the object
    objPrio: {
        0: 15, // used to be importantResults
        // changed 5->7 to generally rank object name matches higher than page term matches
        1: 7,  // used to be objectResults
        2: -5, // used to be unimportantResults
    },
    // Used when the priority is not in the mapping.
    objPrioDefault: 0,

    // query found in title
    title: 15,
    partialTitle: 7,
    // query found in terms
    term: 5,
    partialTerm: 2,
  };
