import http from "k6/http";

export const options = {
  vus: 15,
  duration: "30s",
};
export default function () {
  http.get("http://localhost:3000/v1/match/archive?queue=440");
}
