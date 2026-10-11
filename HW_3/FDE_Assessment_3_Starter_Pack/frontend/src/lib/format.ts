export function formatCurrency(amount: number | null | undefined): string {
  if (amount === null || amount === undefined) {
    return "Undisclosed";
  }
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(amount);
}

export function formatDate(isoString: string | null | undefined): string {
  if (!isoString) {
    return "N/A";
  }
  const dateObj = new Date(isoString);
  if (isNaN(dateObj.getTime())) {
    return isoString;
  }
  return dateObj.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function cleanLabel(raw: string): string {
  const parts = raw.split("_");
  let result = "";
  for (let i = 0; i < parts.length; i++) {
    const word = parts[i];
    if (word.length > 0) {
      const cap = word.charAt(0).toUpperCase() + word.slice(1);
      result = result ? `${result} ${cap}` : cap;
    }
  }
  return result;
}
