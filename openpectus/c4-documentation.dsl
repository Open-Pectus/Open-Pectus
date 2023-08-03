/*
Render:
https://structurizr.com/dsl

Reference:
https://github.com/structurizr/dsl/blob/master/docs/language-reference.md
https://github.com/structurizr/dsl/tree/master/docs/cookbook
*/


workspace {

    model {
        
        user = person "User" "An Open Pectus user."
        openPectusSystem = softwareSystem "Open Pectus" "Manages Open Pectus Engines and Unit Operations." {
            frontend = container "Frontend" "Web Frontend" "Angular"
            aggregator = container "Aggregator" "Manage engines, serve fronend" "Python, FastAPI, Rest, WebSocket"
            database = container "Database" "" "SQLite"
            engine = container "Engine" "Manage unit operation hardware" "Python, FastAPI, Rest, WebSocket" {
                executionEngine = component "ExecutionEngine"
                uod = component "Unit Operation Definition"
                interpreter = component "Interpreter" ""
            }
        }

        hw = softwareSystem "Hardware" "Unit Operation hardware"


        user -> frontend "Uses"

        frontend -> aggregator "Reads data, invokes commands"

        aggregator -> executionEngine "Reads data, invokes commands"
        aggregator -> executionEngine "Receives updates from" {
            tags "WebSocket" 
        }
        aggregator -> database "Persists data to"

        executionEngine -> uod "Uses"
        executionEngine -> interpreter "Controls"

        engine -> hw "Controls [opcua over TCP/IP]"
    }

    views {
        systemContext openPectusSystem {
            include *
            autoLayout
        }

        container openPectusSystem {
            include *
            autoLayout
        }
        
        component engine {
            include *
            autoLayout
        }

        styles {
            element "Software System" {
                background #1168bd
                color #ffffff
            }
            element "Person" {
                shape person
                background #08427b
                color #ffffff
            }
            
            relationship "WebSocket" {
                // color #ff0000
                dashed false
            }        
        }
    }
}