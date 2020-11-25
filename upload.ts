/// <reference path="../models" />

import { API, graphqlOperation } from 'aws-amplify'
import { createBusiness } from './graphql/mutations'
import Business from MSFIDOCredentialAssertion;
const initialState: Business = { name: '', description: '', longDescription: '', type: BusinessType.RESTAURANT }

async function addTodo() {
    try {
        const todo: Business = { ...formState }
        await API.graphql(graphqlOperation(createBusiness, { input: todo }))
    } catch (err) {
        console.log('error creating todo:', err)
    }
}



