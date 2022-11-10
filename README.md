mutation {
  person: createPerson(params: {name:"Jeremy", email:"jeremy@email.com"}) { person { id } }
  asset: createAsset(params: {name:"Database"}) { asset { id } }
  endpoint: createEndpoint(params: {name:"Jeremy's Macbook Pro"}) { endpoint { id } }
  browser: createBrowser(params: {name:"Chrome", major:99, minor: 1}) { browser { id } }
  operatingSystem: createOperatingSystem(params: {name:"MacOS", major:14, minor:1}) { operatingSystem {id}}
  service: createService(params: {name:"Dropbox"}) { service {id}}
  impact: createImpact(params:{name:"Loss of company" value: 999}) {impact { id }}
}