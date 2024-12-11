import { Hsluv } from "./hsluv";

// typeset some latex code using MathJax
export function typeset(code) {
  MathJax.startup.promise = MathJax.startup.promise
    .then(() => MathJax.typesetPromise(code()))
    .catch((err) => console.log("Typeset failed: " + err.message));
  return MathJax.startup.promise;
}

/**
 * Compares the similarity between two strings using an n-gram comparison method.
 * The grams default to length 2.
 * @param {string} str1 The first string to compare.
 * @param {string} str2 The second string to compare.
 * @param {number} gramSize The size of the grams. Defaults to length 2.
 * @returns {number} The similarity between the two strings.
 */
export function stringSimilarity(str1, str2, gramSize = 2) {
  /**
   * @param {string} s The string to get n-grams from.
   * @param {number} len The length of the n-grams.
   * @returns {string[]} An array of n-grams of the given length.
   */
  function getNGrams(s, len) {
    s = " ".repeat(len - 1) + s.toLowerCase() + " ".repeat(len - 1);
    const v = new Array(s.length - len + 1);
    for (let i = 0; i < v.length; i++) v[i] = s.slice(i, i + len);
    return v;
  }

  if (!str1?.length || !str2?.length) return 0.0;

  //Order the strings by length so the order they're passed in doesn't matter
  //and so the smaller string's ngrams are always the ones in the set
  const s1 = str1.length < str2.length ? str1 : str2;
  const s2 = str1.length < str2.length ? str2 : str1;

  const pairs1 = getNGrams(s1, gramSize);
  const pairs2 = getNGrams(s2, gramSize);
  const set = new Set(pairs1);

  let total = pairs2.length,
    hits = 0;
  for (let item of pairs2) if (set.delete(item)) hits++;
  return hits / total;
}

function hashCode(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash |= 0; // Convert to a 32-bit integer
  }
  return hash;
}


export function colorFromId(id) {
  const sample = 360*20;
  const randNum = (hashCode(id) % sample + sample) % sample;
  const hue = randNum%360;
  const l = randNum/360 + 55;
  const hsluv = new Hsluv();
  hsluv.hpluv_h = hue;
  hsluv.hpluv_p = 80;
  hsluv.hpluv_l = l;
  hsluv.hpluvToHex();
  return hsluv.hex;
}