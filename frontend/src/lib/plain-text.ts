/** Strip markdown markers when the UI renders plain text only. */
export function sanitizeMentorText(text: string): string {
  if (!text) return text;
  return text
    .replace(/^#{1,6}\s*/gm, "")
    .replace(/\*\*(.+?)\*\*/g, "$1")
    .replace(/(?<!\*)\*([^*]+)\*(?!\*)/g, "$1")
    .replace(/`([^`]+)`/g, "$1")
    .replace(/[#*]+/g, "")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}
