#!/bin/bash

STACK_NAME="SpaceXFullStack"
MAX_WAIT=1800  # 30 minutos máximo
WAIT_INTERVAL=30
ELAPSED=0

echo "⏳ Monitoreando estado del stack SpaceXFullStack..."
echo "💡 Estado actual: UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS"
echo "📝 CloudFormation está limpiando recursos después del rollback automático"

while [ $ELAPSED -lt $MAX_WAIT ]; do
    STATUS=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --query 'Stacks[0].StackStatus' --output text 2>/dev/null || echo "NOT_FOUND")
    
    case $STATUS in
        "UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS")
            echo "🔄 Still cleaning up... ($((ELAPSED/60))m $((ELAPSED%60))s elapsed)"
            ;;
        "UPDATE_ROLLBACK_COMPLETE")
            echo "✅ ✅ ✅ CLEANUP COMPLETED! Stack is now in UPDATE_ROLLBACK_COMPLETE"
            echo "🚀 Ready for new deployments"
            break
            ;;
        "UPDATE_COMPLETE")
            echo "🎉 Stack deployment completed successfully!"
            break
            ;;
        "NOT_FOUND")
            echo "📭 Stack not found"
            break
            ;;
        *)
            echo "📊 Current status: $STATUS"
            ;;
    esac
    
    sleep $WAIT_INTERVAL
    ELAPSED=$((ELAPSED + WAIT_INTERVAL))
done

if [ $ELAPSED -ge $MAX_WAIT ]; then
    echo "❌ TIMEOUT: Stack stuck in cleanup for too long"
    echo "💡 Manual intervention may be required"
else
    echo "⏰ Total wait time: $((ELAPSED/60)) minutes"
fi