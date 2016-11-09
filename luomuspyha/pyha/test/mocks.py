#coding=utf-8
#json-muotoinen pyyntö
JSON_MOCK = '''
{
	"id": "http://tun.fi/HBF.C60AB314-43E9-41F8-BB7D-0775773B16BD",
	"source": "KE.398",
	"email": "ex.apmle@example.com",
	"personId":"MA.309",
	"approximateMatches": 1742,
	"downloadFormat": "CSV_FLAT",
	"downloadIncludes": [
	  "DOCUMENT_FACTS",
	  "GATHERING_FACTS",
	  "UNIT_FACTS"
	],
	"filters": [
		{
			"target": [
				"linnut",
				"nisäkkäät"
			]
		},
		{
			"time": [
				"2000/"
			]
		}
	],
	"collections": [
		{
			"id": "http://tun.fi/HR.39",
			"count": 1031,
			"secureReasons": [

			"DEFAULT_TAXON_CONSERVATION",

			"CUSTOM",

			"DATA_QUARANTINE_PERIOD"

			]
		},
		{
			"id": "http://tun.fi/HR.447",
			"count": 904,
			"secureReasons": [

			"DEFAULT_TAXON_CONSERVATION",

			"CUSTOM",

			"DATA_QUARANTINE_PERIOD"

			]
		},
		{
			"id": "http://tun.fi/HR.60",
			"count": 14,
			"secureReasons": [

			"DEFAULT_TAXON_CONSERVATION",

			"CUSTOM",

			"DATA_QUARANTINE_PERIOD"

			]
		}
	]
}'''

#eroaa ensimmäisestä id:n osalta
JSON_MOCK2 = '''
{
	"id": "http://tun.fi/HBF.C60AB314-43E9-41F8-BB7D-0775773B16BE",
	"source": "KE.398",
	"email": "ex@example.com",
	"personId":"MA.309",
	"approximateMatches": 1742,
	"downloadFormat": "CSV_FLAT",
	"downloadIncludes": [
	  "DOCUMENT_FACTS",
	  "GATHERING_FACTS",
	  "UNIT_FACTS"
	],
	"filters": [
		{
			"target": [
				"linnut",
				"salaporsaat"
			]
		},
		{
			"time": [
				"2000/"
			]
		}
	],
	"collections": [
		{
			"id": "http://tun.fi/HR.39",
			"count": 1031,
			"secureReasons": [

			"DEFAULT_TAXON_CONSERVATION",

			"CUSTOM",

			"DATA_QUARANTINE_PERIOD"

			]
		},
		{
			"id": "http://tun.fi/HR.447",
			"count": 904,
			"secureReasons": [

			"DEFAULT_TAXON_CONSERVATION",

			"CUSTOM",

			"DATA_QUARANTINE_PERIOD"

			]
		},
		{
			"id": "http://tun.fi/HR.60",
			"count": 14,
			"secureReasons": [

			"DEFAULT_TAXON_CONSERVATION",

			"CUSTOM",

			"DATA_QUARANTINE_PERIOD"

			]
		}
	]
}'''

#jsonista puuttuu filtterit
JSON_MOCK3 = '''
{
	"id": "http://tun.fi/HBF.C60AB314-43E9-41F8-BB7D-0775773B15555",
	"source": "KE.398",
	"email": "filters@example.com",
	"personId":"MA.309",
	"approximateMatches": 1742,
	"downloadFormat": "CSV_FLAT",
	"downloadIncludes": [
	  "DOCUMENT_FACTS",
	  "GATHERING_FACTS",
	  "UNIT_FACTS"
	],
	"collections": [
		{
			"id": "http://tun.fi/HR.39",
			"count": 1031,
			"secureReasons": [

			"DEFAULT_TAXON_CONSERVATION",

			"CUSTOM",

			"DATA_QUARANTINE_PERIOD"

			]
		},
		{
			"id": "http://tun.fi/HR.447",
			"count": 904,
			"secureReasons": [

			"DEFAULT_TAXON_CONSERVATION",

			"CUSTOM",

			"DATA_QUARANTINE_PERIOD"

			]
		},
		{
			"id": "http://tun.fi/HR.60",
			"count": 14,
			"secureReasons": [

			"DEFAULT_TAXON_CONSERVATION",

			"CUSTOM",

			"DATA_QUARANTINE_PERIOD"

			]
		}
	]
}'''

#mock4 on email-testausta varten
JSON_MOCK4 = '''
{
	"id": "http://tun.fi/HBF.C60AB314-43E9-41F8-BB7D-0775773B12LL",
	"description": "Testausta",
	"source": "KE.398",
	"email": "te.staaja@example.com",
	"personId":"MA.309",
	"approximateMatches": 1742,
	"downloadFormat": "CSV_FLAT",
	"downloadIncludes": [
	  "DOCUMENT_FACTS",
	  "GATHERING_FACTS",
	  "UNIT_FACTS"
	],
	"filters": [
		{
			"target": [
				"testilinnut",
				"testinisäkkäät"
			]
		},
		{
			"time": [
				"2000/"
			]
		}
	],
	"collections": [
		{
			"id": "http://tun.fi/HR.39",
			"count": 1031,
			"secureReasons": [

			"DEFAULT_TAXON_CONSERVATION",

			"CUSTOM",

			"DATA_QUARANTINE_PERIOD"

			]
		},
		{
			"id": "http://tun.fi/HR.447",
			"count": 904,
			"secureReasons": [

			"DEFAULT_TAXON_CONSERVATION",

			"CUSTOM",

			"DATA_QUARANTINE_PERIOD"

			]
		},
		{
			"id": "http://tun.fi/HR.60",
			"count": 14,
			"secureReasons": [

			"DEFAULT_TAXON_CONSERVATION",

			"CUSTOM",

			"DATA_QUARANTINE_PERIOD"

			]
		}
	]
}'''
#sama pyyntö kuin mock4, mutta eri id ja kuvaus
JSON_MOCK5 = '''
{
	"id": "http://tun.fi/HBF.C60AB314-43E9-41F8-BB7D-0775773B12LÖ",
	"description": "Testausta2",
	"source": "KE.398",
	"email": "te.staaja@example.com",
	"personId":"MA.309",
	"approximateMatches": 1742,
	"downloadFormat": "CSV_FLAT",
	"downloadIncludes": [
	  "DOCUMENT_FACTS",
	  "GATHERING_FACTS",
	  "UNIT_FACTS"
	],
	"filters": [
		{
			"target": [
				"testilinnut",
				"testinisäkkäät"
			]
		},
		{
			"time": [
				"2000/"
			]
		}
	],
	"collections": [
		{
			"id": "http://tun.fi/HR.39",
			"count": 1031,
			"secureReasons": [

			"DEFAULT_TAXON_CONSERVATION",

			"CUSTOM",

			"DATA_QUARANTINE_PERIOD"

			]
		},
		{
			"id": "http://tun.fi/HR.447",
			"count": 904,
			"secureReasons": [

			"DEFAULT_TAXON_CONSERVATION",

			"CUSTOM",

			"DATA_QUARANTINE_PERIOD"

			]
		},
		{
			"id": "http://tun.fi/HR.60",
			"count": 14,
			"secureReasons": [

			"DEFAULT_TAXON_CONSERVATION",

			"CUSTOM",

			"DATA_QUARANTINE_PERIOD"

			]
		}
	]
}'''
#mock6:sta löytyy secure reasonien määriä
JSON_MOCK6 = '''	
{
	"id": "http://tun.fi/HBF.C60AB314-43E9-41F8-BB7D-0775sdB16BD",
	"source": "KE.398",
	"email": "pyhatestaaja@gmail.com",
	"personId":"MA.309",
	"approximateMatches": 1742,
	"downloadFormat": "CSV_FLAT",
	"downloadIncludes": [
	  "DOCUMENT_FACTS",
	  "GATHERING_FACTS",
	  "UNIT_FACTS"
	],
	"filters": [
		{
			"target": [
				"linnut",
				"nisäkkäät"
			]
		},
		{
			"time": [
				"2000/"
			]
		}
	],
	"collections": [
		{
			"id": "colcustomsec1",
			      "secureReasons": [
        "DATA_QUARANTINE_PERIOD"
      ],
      "mainSecureReasons": {
        "CUSTOM": {
          "count": 1
        }
      }
		},
		{
			"id": "colsecured",
			"secureReasons": [
        "DEFAULT_TAXON_CONSERVATION",
        "CUSTOM",
        "DATA_QUARANTINE_PERIOD"
      ],
      "mainSecureReasons": {
        "DEFAULT_TAXON_CONSERVATION": {
          "count": 3
        },
        "CUSTOM": {
          "count": 2
        }
      }
		}
	]
	}
  '''
