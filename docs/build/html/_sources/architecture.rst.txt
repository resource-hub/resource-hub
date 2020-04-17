Architecture
============

*********
Contracts
*********

Every interaction on Resource Hub is based on contracts: Everything is a contract!
These contracts are produced by contract procedures. They define the framework of potential contracts. Available payment methods, assets, terms and conditions ...


.. figure:: figures/statemachine-contract-procedure.png
   
   The contract procedure as factory for new contracts

Each individual contract is a state machine. The states represent the different stages that have different actions attached to them. Contracts emit events, that decoupled code can listen to. The change of a state is a very fundamental event emitted by a contract. The audience that listens to these events is called Trigger:  Event -> Condition -> Action

.. figure:: figures/statemachine-state-graph.png

**********
Deployment
**********

Currently the application is deployed in a container.

.. figure:: figures/deployment-architecture.png
