// SPDX-License-Identifier: MIT

'use-strict';

let queryBeingDone = undefined;
let pattern = undefined;

const escapedRegex = /[-\/\\^$*+?.()|[\]{}]/g;
function escapeRegex(e) {
    return e.replace(escapedRegex, '\\$&');
}

function __score(haystack, regex) {
    let match = regex.exec(haystack);
    if (match == null) {
        return Number.MAX_VALUE;
    }
    let subLength = match[0].length;
    let start = match.index;
    return (subLength * 1000 + start) / 1000.0;
}

// unused for now
function __cleanNamespaces(query) {
    return query.replace(/(disnake\.(ext\.)?)?(.+)/, '$3');
}

function __setPattern() {
    const params = new URLSearchParams(window.location.search);
    queryBeingDone = params.get('q');
    if (queryBeingDone) {
        pattern = new RegExp(Array.from(queryBeingDone).map(escapeRegex).join('.*?'), 'i');
    } else {
        queryBeingDone = null;
        pattern = null;
    }
}

Scorer = {
    // Implement the following function to further tweak the score for each result
    // The function takes a result array [filename, title, anchor, descr, score]
    // and returns the new score.
    score: (result) => {
        // only inflate the score of things that are actual API reference things
        const [, title, , , score,] = result;

        if (queryBeingDone === undefined) {
            __setPattern();
        }

        if (pattern !== null && title.startsWith('disnake.')) {
            let _score = __score(title, pattern);
            if (_score === Number.MAX_VALUE) {
                return score;
            }
            let newScore = 100 + queryBeingDone.length - _score;
            // console.log(`${title}: ${score} -> ${newScore} (${_score})`);
            return newScore;
        }
        return score;
    },

    // query matches the full name of an object
    objNameMatch: 15,
    // or matches in the last dotted part of the object name
    objPartialMatch: 11,
    // Additive scores depending on the priority of the object
    objPrio: {
        0: 15,  // used to be importantResults
        1: 7,   // used to be objectResults
        2: -5   // used to be unimportantResults
    },
    //  Used when the priority is not in the mapping.
    objPrioDefault: 0,

    // query found in title
    title: 15,
    partialTitle: 7,
    // query found in terms
    term: 5,
    partialTerm: 2
};
