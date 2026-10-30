// Accept integer counts from JSON numbers or digit-only strings consistently.
// Do not coerce booleans, arrays, blanks, fractions, or arbitrary text.
function positiveCount(value) {
  const count = typeof value === 'string' && /^\d+$/.test(value) ? Number(value) : value;
  return Number.isSafeInteger(count) && count > 0 ? count : null;
}

module.exports = { positiveCount };
