from typing import List
from .base import Rule
from .idiomatic_rules import (
    RecursiveCteHierarchyRule,
    WindowFunctionAnalyticsRule,
    UpsertMergeIdempotencyRule,
    MaterializedViewCacheRule,
    LateralJoinSubqueryRule,
    TablePartitioningShardingRule,
)
from .indexing_rules import (
    PartialConditionalIndexRule,
    CoveringIndexIncludeRule,
    GinGistSpecializedIndexRule,
    CompositeMultiColumnIndexRule,
    ForeignKeyCascadeTreeRule,
)
from .procedural_rules import (
    StoredProcedureRouterRule,
    TriggerEventInterceptorRule,
    TransactionIsolationGuardRule,
    AutonomousTransactionSavepointRule,
)
from .creational_rules import (
    FactorySequenceIdGeneratorRule,
    BuilderDynamicQueryComposerRule,
    PrototypeRowClonerRule,
    SingletonConfigParamTableRule,
    AbstractFactorySchemaTenantRule,
)
from .structural_rules import (
    AdapterForeignDataWrapperRule,
    BridgePolymorphicJunctionRule,
    CompositeHierarchicalTreeRule,
    DecoratorComputedAuditLogRule,
    FacadeReportingViewRule,
    FlyweightLookupDictionaryRule,
    ProxyStagedLandingTableRule,
)
from .behavioral_rules import (
    ChainOfResponsibilityTriggerPipelineRule,
    CommandActionQueueTableRule,
    InterpreterDynamicSqlEvalRule,
    IteratorCursorFetchLoopRule,
    MediatorPubsubNotifyRule,
    MementoPointInTimeFlashbackRule,
    ObserverTriggerAuditBroadcastRule,
    StateMachineStatusConstraintRule,
    StrategyDynamicPartitionPruningRule,
    TemplateMethodProceduralSchemaRule,
    VisitorRecursiveTreeScanRule,
)
from .security_rules import (
    SqlInjectionDynamicConcatHazardRule,
    MissingIndexForeignKeyHazardRule,
    NPlusOneCursorIterationHazardRule,
    UnboundedSelectStarHazardRule,
    DeadlockProneLockOrderingHazardRule,
    ImplicitTypeCastingIndexHazardRule,
)
from .solid_principles_rules import (
    MonolithicProcedureSrpRule,
    WideTableGodSchemaSrpRule,
    FatViewInterfaceIspRule,
)


def get_default_rules() -> List[Rule]:
    return [
        # Idiomatic
        RecursiveCteHierarchyRule(),
        WindowFunctionAnalyticsRule(),
        UpsertMergeIdempotencyRule(),
        MaterializedViewCacheRule(),
        LateralJoinSubqueryRule(),
        TablePartitioningShardingRule(),
        # Indexing
        PartialConditionalIndexRule(),
        CoveringIndexIncludeRule(),
        GinGistSpecializedIndexRule(),
        CompositeMultiColumnIndexRule(),
        ForeignKeyCascadeTreeRule(),
        # Procedural
        StoredProcedureRouterRule(),
        TriggerEventInterceptorRule(),
        TransactionIsolationGuardRule(),
        AutonomousTransactionSavepointRule(),
        # Creational
        FactorySequenceIdGeneratorRule(),
        BuilderDynamicQueryComposerRule(),
        PrototypeRowClonerRule(),
        SingletonConfigParamTableRule(),
        AbstractFactorySchemaTenantRule(),
        # Structural
        AdapterForeignDataWrapperRule(),
        BridgePolymorphicJunctionRule(),
        CompositeHierarchicalTreeRule(),
        DecoratorComputedAuditLogRule(),
        FacadeReportingViewRule(),
        FlyweightLookupDictionaryRule(),
        ProxyStagedLandingTableRule(),
        # Behavioral
        ChainOfResponsibilityTriggerPipelineRule(),
        CommandActionQueueTableRule(),
        InterpreterDynamicSqlEvalRule(),
        IteratorCursorFetchLoopRule(),
        MediatorPubsubNotifyRule(),
        MementoPointInTimeFlashbackRule(),
        ObserverTriggerAuditBroadcastRule(),
        StateMachineStatusConstraintRule(),
        StrategyDynamicPartitionPruningRule(),
        TemplateMethodProceduralSchemaRule(),
        VisitorRecursiveTreeScanRule(),
        # Security Hazards
        SqlInjectionDynamicConcatHazardRule(),
        MissingIndexForeignKeyHazardRule(),
        NPlusOneCursorIterationHazardRule(),
        UnboundedSelectStarHazardRule(),
        DeadlockProneLockOrderingHazardRule(),
        ImplicitTypeCastingIndexHazardRule(),
        # SOLID
        MonolithicProcedureSrpRule(),
        WideTableGodSchemaSrpRule(),
        FatViewInterfaceIspRule(),
    ]
