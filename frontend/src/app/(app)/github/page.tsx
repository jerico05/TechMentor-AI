import { redirect } from "next/navigation";

export default function GitHubRedirectPage() {
  redirect("/settings#settings-github");
}
