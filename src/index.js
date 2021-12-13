import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
    
class TermMapper extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            classes: ['class1', 'class2', 'class3'],
            selectedClass: "",
            mappables: [],
            targets: [],
            mappings: {
                'class30': 'class302',
                'class35': 'class358'
            }
        };
    }

    handleSelectClass(name) {
        const newUnmapped = Array(10).fill().map((x, ind) => {return name + ind});

        this.setState({
            selectedClass: name,
            mappables: newUnmapped,
        });
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
                this.state.classes.map((name) => {
                    return (
                        <option 
                            key={name} 
                            onClick={() => this.handleSelectClass(name)}>
                            {name}
                        </option>
                    )
                })
            }
            </select>

            <select size={20}>
            <option disabled value>{ this.state.mappables.length > 0 ? '-- select an option -- ' : ' -- select a class to map -- '}</option>
            {
                this.state.mappables.map((name) => {
                    if (name in this.state.mappings) {
                        return (
                            <option 
                                key={name} 
                                onClick={() => this.handleSelectMappable(name)}
                                style={{color: 'green'}}>
                                {name}
                            </option>
                        )
                    }
                    return (
                        <option 
                            key={name} 
                            onClick={() => this.handleSelectMappable(name)}>
                            {name}
                        </option>
                    )
                    
                })
            }
            </select>

            <select size={20}>
            <option disabled value>{ this.state.mappables.length > 0 ? '-- select an option -- ' : ' -- select a class to map -- '}</option>
            {
                this.state.targets.map((name) => {
                    if (this.state.selectedMappable in this.state.mappings) {
                        if (this.state.mappings[this.state.selectedMappable] === name) {
                            return (
                                <option 
                                    key={name} 
                                    onClick={() => this.handleSelectTarget(name)}
                                    style={{color: 'green'}}>
                                    {name}
                                </option>
                            )
                        }
                    }
                    return (
                        <option 
                            key={name} 
                            onClick={() => this.handleSelectTarget(name)}>
                            {name}
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
        