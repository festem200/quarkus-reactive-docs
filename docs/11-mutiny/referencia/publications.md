# Publications

> **Documentacion oficial:** <https://smallrye.io/smallrye-mutiny/latest/reference/publications>  
> **Fuente:** `documentation/docs/reference/publications.md` en [smallrye/smallrye-mutiny@3.3.0](https://github.com/smallrye/smallrye-mutiny/blob/3.3.0/documentation/docs/reference/publications.md)  
> **Version documentada:** Mutiny 3.3.0 · **Sincronizado:** 2026-08-17 · **Licencia:** Apache-2.0

Julien Ponge, Arthur Navarro, Clément Escoffier, and Frédéric Le Mouël. 2021.
**[Analysing the Performance and Costs of Reactive Programming Libraries in Java](https://doi.org/10.1145/3486605.3486788).**
_In Proceedings of the 8th ACM SIGPLAN International Workshop on Reactive and Event-Based Languages and Systems (REBLS ’21)_, October 18, 2021, Chicago, IL, USA. ACM, New York, NY, USA, 10 pages.
[(PDF)](https://hal.inria.fr/hal-03409277/document)

> Modern services running in cloud and edge environments need to be resource-efficient to increase deployment density and reduce operating costs.
> Asynchronous I/O combined with asynchronous programming provides a solid technical foundation to reach these goals.
> Reactive programming and reactive streams are gaining traction in the Java ecosystem.
> However, reactive streams implementations tend to be complex to work with and maintain.
> This paper discusses the performance of the three major reactive streams compliant libraries used in Java applications: RxJava, Project Reactor, and SmallRye Mutiny.
> As we will show, advanced optimization techniques such as operator fusion do not yield better performance on realistic I/O-bound workloads, and they significantly increase development and maintenance costs.
