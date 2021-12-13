import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';

const apiEndpoint = 'http://localhost:5000'

function do_request(method, endpoint, handler, payload = null) {
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
            selectedClass: "",
            mappables: [],
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
        let formData = new FormData();
        formData.append('type', name);

        // let body = 'type=' + name;

        do_request(
            'POST', 
            '/values', (json) => {
                this.setState({
                    selectedClass: name,
                    mappables: json.localValues,
                    targets: json.targets,
                    mappings: json.mappings
                })
            },
            formData
        );
    }

    handleSelectMappable(name) {
        const newTarget = Array(10).fill().map((x, ind) => {return name + ind});

        this.setState({
            selectedMappable: name,
            targets: newTarget,
        });
    }

    handleSelectTarget(name) {
        const newMappings = this.state.mappings;
        newMappings[this.state.selectedMappable] = name;

        this.setState({
            mappings: newMappings
        });
    }

    render() {
        return (
            <div className={"Termmapper"}>
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

            <select size={20}>
            <option disabled value>{ this.state.mappables.length > 0 ? '-- select an option -- ' : ' -- select a class to map -- '}</option>
            {
                this.state.mappables.map((value) => {
                    if (value in this.state.mappings) {
                        return (
                            <option 
                                key={value} 
                                onClick={() => this.handleSelectMappable(value)}
                                style={{color: 'green'}}>
                                {value}
                            </option>
                        )
                    }
                    return (
                        <option 
                                key={value} 
                                onClick={() => this.handleSelectMappable(value)}>
                                {value}
                        </option>
                    )
                    
                })
            }
            </select>

            <select size={20}>
            <option disabled value>{ this.state.mappables.length > 0 ? '-- select an option -- ' : ' -- select a class to map -- '}</option>
            {
                this.state.targets.map((el) => {
                    if (this.state.selectedMappable in this.state.mappings) {
                        if (this.state.mappings[this.state.selectedMappable] === el.uri) {
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
        