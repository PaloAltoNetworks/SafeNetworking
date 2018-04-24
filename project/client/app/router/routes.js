export default [
  {
    name: "dashboard",
    path: "/"
  },
  {
    name: "admin",
    path: "/admin"
  },
  {
    name: "iot",
    path: "/iot",
    children: [
      { name: "dashboard", path: "/dashboard" },
      { name: "child-route", path: "/child-route" }
    ]
  },
  {
    name: "faq",
    path: "/faq"
  },
  {
    name: "domain",
    path: "/domain",
  
  children: [
    { name: "dashboard", path: "/dashboard" },
    { name: "malware-resolvers", path: "/malware-resolvers" },
    { name: "malware-dns-resolver", path: "/malware-dns-resolver" },
    { name: "malware-by-file", path: "/malware-by-file"},
    { name: "at-risk-clients", path: "/at-risk-clients"},
    { name: "top-10-malware", path: "/top-10-malware"}
  ]
}
];
