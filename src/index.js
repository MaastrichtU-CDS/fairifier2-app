import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';

const apiEndpoint = 'http://localhost:5000'

function do_request(method, endpoint, handler, payload = null) {
    /**
     * Helper function to communicate with the underlying API
     * @param {string} method 'POST' or 'GET'
     * @param {string} endpoint the endpoint to communicate with e.g. /values
     * @param {function} handler the function that gets passed the returned JSON and handles it
     * @param {dict} payload (optional) POST content if relevant
     */
    var xhr = new XMLHttpRequest();

    xhr.addEventListener("readystatechange", () => {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                var response = xhr.responseText;
                var json = JSON.parse(response);
                
                handler(json);
            }
        }
    });

    xhr.open(method, apiEndpoint + endpoint);
    xhr.send(payload);
}
    
class TermMapper extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            classes: [],
            selectedClass: null,
            localVals: [],
            selectedLocalVal: null,
            targets: [],
            mappings: {}
        };
    }

    componentDidMount() {
        do_request('GET', '/classes', (json) => {
            this.setState({
                classes: json.classes
            });
        });
    }

    handleSelectClass(name) {
        /**
         * Handle selecting of a class (which has local values attached to it).
         * Gets all local values and potential target classes associated with it.
         * @param {string} name name (unique) of the selected class
         */
        let formData = new FormData();
        formData.append('class', name);

        do_request(
            'POST', 
            '/values', (json) => {
                this.setState({
                    selectedClass: name,
                    localVals: json.localValues,
                    selectedLocalVal: null,
                    targets: json.targets,
                    mappings: json.mappings
                })
            },
            formData
        );
    }

    handleSelectLocalVal(name) {
        /**
         * Handles the selection of a local value being selected.
         * @param {string} name name (unique) of the selected class
         */
        this.setState({
            selectedLocalVal: name,
        });
    }

    handleSelectTarget(name) {
        /**
         * Handles the selection of a target class. Takes the combination of
         * class + local value + target class and pushes it to the database
         * for further use.
         * @param {string} name name (unique) of the selected class
         */
        if (this.state.selectedLocalVal) {
            let formData = new FormData();
            formData.append('class', this.state.selectedClass);
            formData.append('value', this.state.selectedLocalVal);
            formData.append('target', name);

            do_request(
                'POST',
                '/add-mapping', 
                (json) => {
                    this.setState({
                        mappings: json.mappings
                    });
                },
                formData
            );
        }
    }

    render() {
        return (
            <div className={"Termmapper"}>

            {/* Class select */}
            <select size={20}>
            <option disabled value> -- select an option -- </option>
            {
                this.state.classes.map((el) => {
                    return (
                        <option 
                            key={el.uri} 
                            onClick={() => this.handleSelectClass(el.uri)}>
                            {'label' in el ? el.label : el.uri}
                        </option>
                    )
                })
            }
            </select>

            {/* Local value select */}
            <select size={20}>
            <option disabled value>{ this.state.localVals.length > 0 ? '-- select an option -- ' : ' -- select a class to map -- '}</option>
            {
                this.state.localVals.map((value) => {
                    // Display local value, colour it green if a mapping exists for it
                    if (value in this.state.mappings) {
                        return (
                            <option 
                                key={value} 
                                onClick={() => this.handleSelectLocalVal(value)}
                                style={{color: 'green'}}>
                                {value}
                            </option>
                        )
                    }
                    return (
                        <option 
                                key={value} 
                                onClick={() => this.handleSelectLocalVal(value)}>
                                {value}
                        </option>
                    )
                    
                })
            }
            </select>

            {/* Target class select */}
            <select size={20}>
            <option disabled value>{ this.state.localVals.length > 0 ? '-- select an option -- ' : ' -- select a class to map -- '}</option>
            {
                this.state.targets.map((el) => {
                    // Display the target class, colour it green if a mapping exists
                    // for the currently selected local value mapped to this target value
                    if (this.state.selectedLocalVal in this.state.mappings) {
                        if (this.state.mappings[this.state.selectedLocalVal] === el.uri) {
                            return (
                                <option 
                                    key={el.uri} 
                                    onClick={() => this.handleSelectTarget(el.uri)}
                                    style={{color: 'green'}}>
                                    {'label' in el ? el.label : el.uri}
                                </option>
                            )
                        }
                    }
                    return (
                        <option 
                            key={el.uri} 
                            onClick={() => this.handleSelectTarget(el.uri)}>
                            {'label' in el ? el.label : el.uri}
                        </option>
                    )
                    
                })
            }
            </select>

            </div>

            );
        }
    }
    
    // ========================================
    
ReactDOM.render(
    <TermMapper />,
    document.getElementById('root')
    );
        