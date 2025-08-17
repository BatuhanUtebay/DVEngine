// dvge/core/advanced_combat_engine.js

/**
 * Advanced Turn-Based Combat Engine for DVGE
 * Provides detailed combat mechanics with skills, status effects, and AI
 */

class AdvancedCombatEngine {
    constructor() {
        this.isActive = false;
        this.currentCombat = null;
        this.turnQueue = [];
        this.currentTurnIndex = 0;
        this.animationQueue = [];
        this.skillDatabase = new Map();
        this.statusEffectDatabase = new Map();
        
        this.initializeSkillDatabase();
        this.initializeStatusEffects();
    }
    
    initializeSkillDatabase() {
        // Basic Attack
        this.skillDatabase.set('basic_attack', {
            id: 'basic_attack',
            name: 'Attack',
            description: 'A basic physical attack',
            mana_cost: 0,
            target_type: 'single_enemy',
            damage: 'strength * 1.2 + 10',
            damage_type: 'physical',
            accuracy: 95,
            critical_chance: 5,
            animation: 'slash'
        });
        
        // Fireball
        this.skillDatabase.set('fireball', {
            id: 'fireball',
            name: 'Fireball',
            description: 'Launch a fiery projectile at an enemy',
            mana_cost: 15,
            target_type: 'single_enemy',
            damage: 'intelligence * 1.5 + 20',
            damage_type: 'fire',
            accuracy: 90,
            critical_chance: 10,
            status_effects: [{ id: 'burn', chance: 30, duration: 3 }],
            animation: 'fireball'
        });
        
        // Heal
        this.skillDatabase.set('heal', {
            id: 'heal',
            name: 'Heal',
            description: 'Restore health to an ally',
            mana_cost: 12,
            target_type: 'single_ally',
            healing: 'intelligence * 1.3 + 25',
            accuracy: 100,
            animation: 'heal_sparkle'
        });
        
        // Lightning Bolt
        this.skillDatabase.set('lightning_bolt', {
            id: 'lightning_bolt',
            name: 'Lightning Bolt',
            description: 'Strike with electrical energy',
            mana_cost: 18,
            target_type: 'single_enemy',
            damage: 'intelligence * 1.4 + 15',
            damage_type: 'lightning',
            accuracy: 95,
            critical_chance: 15,
            status_effects: [{ id: 'stun', chance: 25, duration: 1 }],
            animation: 'lightning'
        });
        
        // Shield Bash
        this.skillDatabase.set('shield_bash', {
            id: 'shield_bash',
            name: 'Shield Bash',
            description: 'Bash with shield, chance to stun',
            mana_cost: 8,
            target_type: 'single_enemy',
            damage: 'strength * 0.8 + 15',
            damage_type: 'physical',
            accuracy: 90,
            status_effects: [{ id: 'stun', chance: 40, duration: 1 }],
            animation: 'shield_bash'
        });
        
        // Ice Shard
        this.skillDatabase.set('ice_shard', {
            id: 'ice_shard',
            name: 'Ice Shard',
            description: 'Launch sharp ice at enemy',
            mana_cost: 10,
            target_type: 'single_enemy',
            damage: 'intelligence * 1.1 + 12',
            damage_type: 'ice',
            accuracy: 92,
            status_effects: [{ id: 'slow', chance: 35, duration: 2 }],
            animation: 'ice_shard'
        });
        
        // Power Strike
        this.skillDatabase.set('power_strike', {
            id: 'power_strike',
            name: 'Power Strike',
            description: 'A devastating physical attack',
            mana_cost: 20,
            target_type: 'single_enemy',
            damage: 'strength * 2.0 + 30',
            damage_type: 'physical',
            accuracy: 80,
            critical_chance: 20,
            animation: 'power_strike'
        });
        
        // Group Heal
        this.skillDatabase.set('group_heal', {
            id: 'group_heal',
            name: 'Group Heal',
            description: 'Heal all allies',
            mana_cost: 25,
            target_type: 'all_allies',
            healing: 'intelligence * 1.0 + 15',
            accuracy: 100,
            animation: 'group_heal'
        });
    }
    
    initializeStatusEffects() {
        // Burn
        this.statusEffectDatabase.set('burn', {
            id: 'burn',
            name: 'Burning',
            description: 'Taking fire damage each turn',
            type: 'debuff',
            damage_over_time: 8,
            icon: '🔥',
            color: '#ff4444'
        });
        
        // Stun
        this.statusEffectDatabase.set('stun', {
            id: 'stun',
            name: 'Stunned',
            description: 'Cannot act this turn',
            type: 'debuff',
            prevents_action: true,
            icon: '💫',
            color: '#ffff44'
        });
        
        // Slow
        this.statusEffectDatabase.set('slow', {
            id: 'slow',
            name: 'Slowed',
            description: 'Reduced agility',
            type: 'debuff',
            stat_modifiers: { agility: -3 },
            icon: '🐌',
            color: '#4444ff'
        });
        
        // Poison
        this.statusEffectDatabase.set('poison', {
            id: 'poison',
            name: 'Poisoned',
            description: 'Taking poison damage each turn',
            type: 'debuff',
            damage_over_time: 5,
            icon: '☠️',
            color: '#44ff44'
        });
        
        // Blessed
        this.statusEffectDatabase.set('blessed', {
            id: 'blessed',
            name: 'Blessed',
            description: 'Increased damage and accuracy',
            type: 'buff',
            stat_modifiers: { strength: 2, intelligence: 2 },
            accuracy_bonus: 10,
            icon: '✨',
            color: '#ffffff'
        });
        
        // Shield
        this.statusEffectDatabase.set('shield', {
            id: 'shield',
            name: 'Shielded',
            description: 'Reduced incoming damage',
            type: 'buff',
            damage_reduction: 0.5,
            icon: '🛡️',
            color: '#aaaaaa'
        });
    }
    
    startCombat(combatData, playerParty, gameState) {
        this.isActive = true;
        this.currentCombat = {
            data: combatData,
            turn: 1,
            playerParty: this.initializeParty(playerParty, 'player'),
            enemies: this.initializeParty(combatData.enemies, 'enemy'),
            allies: this.initializeParty(combatData.allies || [], 'ally'),
            environmental_effects: combatData.environmental_effects || [],
            battlefield_state: {
                weather: combatData.weather || 'clear',
                environment: combatData.environment || 'default',
                terrain_effects: combatData.terrain_effects || []
            }
        };
        
        this.createCombatUI();
        this.calculateTurnOrder();
        this.startTurn();
        
        return true;
    }
    
    initializeParty(partyData, type) {
        return partyData.map((member, index) => ({
            ...member,
            id: member.id || `${type}_${index}`,
            type: type,
            current_health: member.health || member.max_health,
            current_mana: member.mana || member.max_mana,
            status_effects: [],
            cooldowns: new Map(),
            position: member.position || (type === 'player' ? 'front' : 'front'),
            ai: type !== 'player' ? new CombatAI(member.ai_type || 'balanced') : null
        }));
    }
    
    createCombatUI() {
        // Remove existing combat UI
        const existing = document.getElementById('advanced-combat-interface');
        if (existing) existing.remove();
        
        const combatInterface = document.createElement('div');
        combatInterface.id = 'advanced-combat-interface';
        combatInterface.className = 'advanced-combat-interface';
        
        combatInterface.innerHTML = `
            <div class="combat-header">
                <div class="combat-title">⚔️ Combat - Turn ${this.currentCombat.turn}</div>
                <div class="combat-info">
                    <span class="weather-info">🌤️ ${this.currentCombat.battlefield_state.weather}</span>
                    <span class="environment-info">🏞️ ${this.currentCombat.battlefield_state.environment}</span>
                </div>
            </div>
            
            <div class="combat-battlefield">
                <div class="enemy-area">
                    <h3>🏴 Enemies</h3>
                    <div class="combatants-grid" id="enemies-grid"></div>
                </div>
                
                <div class="battlefield-center">
                    <div class="environmental-effects" id="environmental-effects"></div>
                    <div class="combat-log" id="combat-log">
                        <div class="log-entry">Combat begins!</div>
                    </div>
                </div>
                
                <div class="player-area">
                    <h3>🛡️ Your Party</h3>
                    <div class="combatants-grid" id="party-grid"></div>
                </div>
            </div>
            
            <div class="combat-controls">
                <div class="current-actor-info" id="current-actor-info"></div>
                <div class="action-buttons" id="action-buttons"></div>
            </div>
        `;
        
        document.body.appendChild(combatInterface);
        this.updateCombatDisplay();
    }
    
    updateCombatDisplay() {
        this.updateCombatantsDisplay();
        this.updateEnvironmentalEffects();
        this.updateCurrentActorInfo();
    }
    
    updateCombatantsDisplay() {
        // Update enemies
        const enemiesGrid = document.getElementById('enemies-grid');
        enemiesGrid.innerHTML = '';
        this.currentCombat.enemies.forEach((enemy, index) => {
            const enemyElement = this.createCombatantElement(enemy, index);
            enemiesGrid.appendChild(enemyElement);
        });
        
        // Update player party
        const partyGrid = document.getElementById('party-grid');
        partyGrid.innerHTML = '';
        this.currentCombat.playerParty.forEach((member, index) => {
            const memberElement = this.createCombatantElement(member, index);
            partyGrid.appendChild(memberElement);
        });
        
        // Update allies if any
        this.currentCombat.allies.forEach((ally, index) => {
            const allyElement = this.createCombatantElement(ally, index);
            partyGrid.appendChild(allyElement);
        });
    }
    
    createCombatantElement(combatant, index) {
        const healthPercent = (combatant.current_health / combatant.max_health) * 100;
        const manaPercent = combatant.max_mana > 0 ? (combatant.current_mana / combatant.max_mana) * 100 : 0;
        
        const element = document.createElement('div');
        element.className = `combatant ${combatant.type}`;
        element.id = `combatant-${combatant.id}`;
        
        // Status effects display
        const statusEffectsHTML = combatant.status_effects.map(effect => {
            const effectData = this.statusEffectDatabase.get(effect.id) || {};
            return `<span class="status-effect" title="${effectData.description || ''}">${effectData.icon || '⚡'}</span>`;
        }).join('');
        
        element.innerHTML = `
            <div class="combatant-portrait">
                <div class="combatant-name">${combatant.name}</div>
                <div class="combatant-level">Lv.${combatant.level || 1}</div>
                ${combatant.type === 'enemy' ? '<div class="target-indicator" onclick="advancedCombat.selectTarget(\'' + combatant.id + '\')">🎯</div>' : ''}
            </div>
            <div class="combatant-stats">
                <div class="health-bar">
                    <div class="bar-label">HP</div>
                    <div class="bar">
                        <div class="bar-fill health-fill" style="width: ${healthPercent}%"></div>
                        <div class="bar-text">${combatant.current_health}/${combatant.max_health}</div>
                    </div>
                </div>
                ${combatant.max_mana > 0 ? `
                <div class="mana-bar">
                    <div class="bar-label">MP</div>
                    <div class="bar">
                        <div class="bar-fill mana-fill" style="width: ${manaPercent}%"></div>
                        <div class="bar-text">${combatant.current_mana}/${combatant.max_mana}</div>
                    </div>
                </div>` : ''}
                <div class="status-effects">${statusEffectsHTML}</div>
            </div>
        `;
        
        return element;
    }
    
    calculateTurnOrder() {
        const allCombatants = [
            ...this.currentCombat.playerParty,
            ...this.currentCombat.enemies,
            ...this.currentCombat.allies
        ].filter(c => c.current_health > 0);
        
        // Sort by agility + random factor
        this.turnQueue = allCombatants.sort((a, b) => {
            const aInitiative = (a.stats?.agility || 10) + Math.random() * 5;
            const bInitiative = (b.stats?.agility || 10) + Math.random() * 5;
            return bInitiative - aInitiative;
        });
        
        this.currentTurnIndex = 0;
    }
    
    startTurn() {
        if (!this.isActive) return;
        
        // Check win/lose conditions
        if (this.checkCombatEnd()) return;
        
        // Process environmental effects
        this.processEnvironmentalEffects();
        
        // Get current actor
        const currentActor = this.getCurrentActor();
        if (!currentActor) {
            this.nextTurn();
            return;
        }
        
        // Process status effects
        this.processStatusEffects(currentActor);
        
        // Check if actor can act
        if (!this.canActorAct(currentActor)) {
            this.logCombatEvent(`${currentActor.name} is unable to act this turn!`);
            this.nextTurn();
            return;
        }
        
        // Handle turn based on actor type
        if (currentActor.type === 'player') {
            this.handlePlayerTurn(currentActor);
        } else {
            this.handleAITurn(currentActor);
        }
    }
    
    getCurrentActor() {
        if (this.currentTurnIndex >= this.turnQueue.length) {
            return null;
        }
        return this.turnQueue[this.currentTurnIndex];
    }
    
    canActorAct(actor) {
        // Check if stunned or has other preventing status effects
        return !actor.status_effects.some(effect => {
            const effectData = this.statusEffectDatabase.get(effect.id);
            return effectData?.prevents_action;
        });
    }
    
    handlePlayerTurn(player) {
        this.updateCurrentActorInfo();
        this.createActionButtons(player);
        this.logCombatEvent(`${player.name}'s turn!`);
    }
    
    updateCurrentActorInfo() {
        const currentActor = this.getCurrentActor();
        const infoElement = document.getElementById('current-actor-info');
        
        if (currentActor) {
            infoElement.innerHTML = `
                <div class="actor-name">${currentActor.name}'s Turn</div>
                <div class="actor-stats-mini">
                    HP: ${currentActor.current_health}/${currentActor.max_health} | 
                    MP: ${currentActor.current_mana}/${currentActor.max_mana}
                </div>
            `;
        }
    }
    
    createActionButtons(player) {
        const buttonsContainer = document.getElementById('action-buttons');
        buttonsContainer.innerHTML = '';
        
        // Basic attack
        const attackBtn = document.createElement('button');
        attackBtn.textContent = '⚔️ Attack';
        attackBtn.className = 'action-button attack-button';
        attackBtn.onclick = () => this.selectAction('basic_attack');
        buttonsContainer.appendChild(attackBtn);
        
        // Skills
        const skillsContainer = document.createElement('div');
        skillsContainer.className = 'skills-container';
        
        (player.skills || []).forEach(skillId => {
            if (skillId === 'basic_attack') return; // Already added
            
            const skill = this.skillDatabase.get(skillId);
            if (!skill) return;
            
            const canUse = this.canUseSkill(player, skill);
            const skillBtn = document.createElement('button');
            skillBtn.textContent = `✨ ${skill.name} (${skill.mana_cost} MP)`;
            skillBtn.className = `action-button skill-button ${canUse ? '' : 'disabled'}`;
            skillBtn.disabled = !canUse;
            skillBtn.title = skill.description;
            
            if (canUse) {
                skillBtn.onclick = () => this.selectAction(skillId);
            }
            
            skillsContainer.appendChild(skillBtn);
        });
        
        buttonsContainer.appendChild(skillsContainer);
        
        // Other actions
        const otherActionsContainer = document.createElement('div');
        otherActionsContainer.className = 'other-actions-container';
        
        // Defend
        const defendBtn = document.createElement('button');
        defendBtn.textContent = '🛡️ Defend';
        defendBtn.className = 'action-button defend-button';
        defendBtn.onclick = () => this.executeAction(player, { type: 'defend' });
        otherActionsContainer.appendChild(defendBtn);
        
        // Escape (if allowed)
        if (this.currentCombat.data.allow_escape) {
            const escapeBtn = document.createElement('button');
            escapeBtn.textContent = '💨 Escape';
            escapeBtn.className = 'action-button escape-button';
            escapeBtn.onclick = () => this.attemptEscape();
            otherActionsContainer.appendChild(escapeBtn);
        }
        
        buttonsContainer.appendChild(otherActionsContainer);
    }
    
    canUseSkill(actor, skill) {
        // Check mana cost
        if (skill.mana_cost > actor.current_mana) return false;
        
        // Check cooldown
        if (actor.cooldowns.has(skill.id) && actor.cooldowns.get(skill.id) > 0) return false;
        
        // Check other requirements
        if (skill.health_cost && skill.health_cost >= actor.current_health) return false;
        
        return true;
    }
    
    selectAction(skillId) {
        const currentActor = this.getCurrentActor();
        const skill = this.skillDatabase.get(skillId);
        
        if (!skill || !this.canUseSkill(currentActor, skill)) return;
        
        // If skill requires target selection, show target selection
        if (this.requiresTargetSelection(skill)) {
            this.showTargetSelection(skill);
        } else {
            // Execute immediately for self-targeting or no-target skills
            this.executeAction(currentActor, { type: 'skill', skill: skill });
        }
    }
    
    requiresTargetSelection(skill) {
        return ['single_enemy', 'single_ally'].includes(skill.target_type);
    }
    
    showTargetSelection(skill) {
        // Highlight valid targets
        this.clearTargetHighlights();
        
        const validTargets = this.getValidTargets(skill);
        validTargets.forEach(target => {
            const element = document.getElementById(`combatant-${target.id}`);
            if (element) {
                element.classList.add('valid-target');
                element.onclick = () => this.executeActionWithTarget(skill, target);
            }
        });
        
        // Show instruction
        this.logCombatEvent(`Select a target for ${skill.name}`);
    }
    
    getValidTargets(skill) {
        switch (skill.target_type) {
            case 'single_enemy':
                return this.currentCombat.enemies.filter(e => e.current_health > 0);
            case 'single_ally':
                return [...this.currentCombat.playerParty, ...this.currentCombat.allies]
                    .filter(a => a.current_health > 0);
            case 'self':
                return [this.getCurrentActor()];
            default:
                return [];
        }
    }
    
    executeActionWithTarget(skill, target) {
        const currentActor = this.getCurrentActor();
        this.clearTargetHighlights();
        this.executeAction(currentActor, { type: 'skill', skill: skill, target: target });
    }
    
    clearTargetHighlights() {
        document.querySelectorAll('.combatant').forEach(el => {
            el.classList.remove('valid-target');
            el.onclick = null;
        });
    }
    
    executeAction(actor, action) {
        switch (action.type) {
            case 'skill':
                this.executeSkill(actor, action.skill, action.target);
                break;
            case 'defend':
                this.executeDefend(actor);
                break;
            case 'wait':
                this.executeWait(actor);
                break;
        }
        
        this.nextTurn();
    }
    
    executeSkill(actor, skill, target = null) {
        // Deduct costs
        actor.current_mana = Math.max(0, actor.current_mana - skill.mana_cost);
        
        // Set cooldown
        if (skill.cooldown > 0) {
            actor.cooldowns.set(skill.id, skill.cooldown);
        }
        
        // Determine targets
        const targets = this.resolveTargets(skill, target);
        
        targets.forEach(targetCombatant => {
            this.executeSkillOnTarget(actor, skill, targetCombatant);
        });
        
        this.logCombatEvent(`${actor.name} uses ${skill.name}!`);
        this.updateCombatDisplay();
    }
    
    resolveTargets(skill, specificTarget) {
        switch (skill.target_type) {
            case 'single_enemy':
            case 'single_ally':
            case 'self':
                return specificTarget ? [specificTarget] : [];
            case 'all_enemies':
                return this.currentCombat.enemies.filter(e => e.current_health > 0);
            case 'all_allies':
                return [...this.currentCombat.playerParty, ...this.currentCombat.allies]
                    .filter(a => a.current_health > 0);
            case 'all':
                return [...this.currentCombat.playerParty, ...this.currentCombat.enemies, ...this.currentCombat.allies]
                    .filter(c => c.current_health > 0);
            default:
                return [];
        }
    }
    
    executeSkillOnTarget(actor, skill, target) {
        // Calculate hit chance
        const hitRoll = Math.random() * 100;
        const accuracy = skill.accuracy + this.getAccuracyModifiers(actor);
        
        if (hitRoll > accuracy) {
            this.logCombatEvent(`${skill.name} missed ${target.name}!`);
            return;
        }
        
        // Calculate damage
        if (skill.damage) {
            const damage = this.calculateDamage(actor, skill, target);
            const isCritical = Math.random() * 100 < (skill.critical_chance || 0);
            const finalDamage = isCritical ? Math.floor(damage * (skill.critical_multiplier || 2)) : damage;
            
            target.current_health = Math.max(0, target.current_health - finalDamage);
            
            this.logCombatEvent(
                `${target.name} takes ${finalDamage} ${skill.damage_type || 'physical'} damage${isCritical ? ' (Critical!)' : ''}!`
            );
            
            this.animateDamage(target, finalDamage, isCritical);
        }
        
        // Calculate healing
        if (skill.healing) {
            const healing = this.calculateHealing(actor, skill, target);
            target.current_health = Math.min(target.max_health, target.current_health + healing);
            
            this.logCombatEvent(`${target.name} recovers ${healing} health!`);
            this.animateHealing(target, healing);
        }
        
        // Apply status effects
        if (skill.status_effects) {
            skill.status_effects.forEach(effectConfig => {
                if (Math.random() * 100 < (effectConfig.chance || 100)) {
                    this.applyStatusEffect(target, effectConfig);
                }
            });
        }
    }
    
    calculateDamage(attacker, skill, target) {
        const baseDamage = this.evaluateDamageFormula(skill.damage, attacker);
        
        // Apply resistances/weaknesses
        let multiplier = 1.0;
        if (target.resistances && target.resistances[skill.damage_type]) {
            multiplier *= (1 - target.resistances[skill.damage_type]);
        }
        if (target.weaknesses && target.weaknesses[skill.damage_type]) {
            multiplier *= (1 + target.weaknesses[skill.damage_type]);
        }
        
        // Apply status effect modifiers
        attacker.status_effects.forEach(effect => {
            const effectData = this.statusEffectDatabase.get(effect.id);
            if (effectData?.stat_modifiers?.strength) {
                multiplier *= (1 + effectData.stat_modifiers.strength * 0.1);
            }
        });
        
        return Math.max(1, Math.floor(baseDamage * multiplier));
    }
    
    evaluateDamageFormula(formula, actor) {
        // Simple formula evaluation
        const stats = actor.stats || {};
        const variables = {
            strength: stats.strength || 10,
            intelligence: stats.intelligence || 10,
            agility: stats.agility || 10,
            vitality: stats.vitality || 10,
            luck: stats.luck || 10
        };
        
        try {
            // Replace variables in formula
            let evalFormula = formula;
            Object.keys(variables).forEach(stat => {
                evalFormula = evalFormula.replace(new RegExp(stat, 'g'), variables[stat]);
            });
            
            // Safely evaluate mathematical expression
            return Math.floor(eval(evalFormula));
        } catch (e) {
            console.warn('Failed to evaluate damage formula:', formula);
            return 10; // Fallback damage
        }
    }
    
    calculateHealing(healer, skill, target) {
        return this.evaluateDamageFormula(skill.healing, healer);
    }
    
    getAccuracyModifiers(actor) {
        let modifier = 0;
        actor.status_effects.forEach(effect => {
            const effectData = this.statusEffectDatabase.get(effect.id);
            if (effectData?.accuracy_bonus) {
                modifier += effectData.accuracy_bonus;
            }
        });
        return modifier;
    }
    
    applyStatusEffect(target, effectConfig) {
        const existingEffect = target.status_effects.find(e => e.id === effectConfig.id);
        
        if (existingEffect) {
            // Refresh duration or stack if allowed
            const effectData = this.statusEffectDatabase.get(effectConfig.id);
            if (effectData?.stackable) {
                existingEffect.stacks = (existingEffect.stacks || 1) + 1;
            }
            existingEffect.duration = effectConfig.duration || 3;
        } else {
            // Add new effect
            target.status_effects.push({
                id: effectConfig.id,
                duration: effectConfig.duration || 3,
                stacks: 1
            });
        }
        
        const effectData = this.statusEffectDatabase.get(effectConfig.id);
        this.logCombatEvent(`${target.name} is affected by ${effectData?.name || effectConfig.id}!`);
    }
    
    processStatusEffects(actor) {
        const effectsToRemove = [];
        
        actor.status_effects.forEach((effect, index) => {
            const effectData = this.statusEffectDatabase.get(effect.id);
            
            if (effectData?.damage_over_time) {
                const damage = effectData.damage_over_time * (effect.stacks || 1);
                actor.current_health = Math.max(0, actor.current_health - damage);
                this.logCombatEvent(`${actor.name} takes ${damage} damage from ${effectData.name}!`);
                this.animateDamage(actor, damage, false);
            }
            
            if (effectData?.healing_over_time) {
                const healing = effectData.healing_over_time * (effect.stacks || 1);
                actor.current_health = Math.min(actor.max_health, actor.current_health + healing);
                this.logCombatEvent(`${actor.name} recovers ${healing} health from ${effectData.name}!`);
                this.animateHealing(actor, healing);
            }
            
            // Reduce duration
            effect.duration--;
            if (effect.duration <= 0) {
                effectsToRemove.push(index);
                this.logCombatEvent(`${effectData?.name || effect.id} effect wears off from ${actor.name}!`);
            }
        });
        
        // Remove expired effects
        effectsToRemove.reverse().forEach(index => {
            actor.status_effects.splice(index, 1);
        });
        
        // Process cooldowns
        for (let [skillId, cooldown] of actor.cooldowns) {
            if (cooldown > 0) {
                actor.cooldowns.set(skillId, cooldown - 1);
            } else {
                actor.cooldowns.delete(skillId);
            }
        }
    }
    
    handleAITurn(aiActor) {
        setTimeout(() => {
            const action = aiActor.ai.chooseAction(
                aiActor,
                this.getAllies(aiActor),
                this.getEnemies(aiActor),
                this.currentCombat.battlefield_state
            );
            
            this.executeAIAction(aiActor, action);
        }, 1000); // Delay for dramatic effect
    }
    
    executeAIAction(actor, action) {
        if (action.type === 'attack') {
            const skill = this.skillDatabase.get(action.skill || 'basic_attack');
            if (skill && action.target) {
                this.executeSkill(actor, skill, action.target);
            }
        } else if (action.type === 'defend') {
            this.executeDefend(actor);
        } else {
            this.executeWait(actor);
        }
        
        this.nextTurn();
    }
    
    getAllies(actor) {
        if (actor.type === 'enemy') {
            return this.currentCombat.enemies.filter(e => e.id !== actor.id && e.current_health > 0);
        } else {
            return [...this.currentCombat.playerParty, ...this.currentCombat.allies]
                .filter(a => a.id !== actor.id && a.current_health > 0);
        }
    }
    
    getEnemies(actor) {
        if (actor.type === 'enemy') {
            return [...this.currentCombat.playerParty, ...this.currentCombat.allies]
                .filter(a => a.current_health > 0);
        } else {
            return this.currentCombat.enemies.filter(e => e.current_health > 0);
        }
    }
    
    executeDefend(actor) {
        // Apply defense bonus for this turn
        this.applyStatusEffect(actor, {
            id: 'defending',
            duration: 1
        });
        
        this.logCombatEvent(`${actor.name} takes a defensive stance!`);
    }
    
    executeWait(actor) {
        this.logCombatEvent(`${actor.name} waits...`);
    }
    
    nextTurn() {
        this.currentTurnIndex++;
        
        if (this.currentTurnIndex >= this.turnQueue.length) {
            // End of round
            this.currentTurnIndex = 0;
            this.currentCombat.turn++;
            this.updateCombatHeader();
            
            // Remove dead combatants from turn queue
            this.turnQueue = this.turnQueue.filter(c => c.current_health > 0);
            
            if (this.turnQueue.length === 0) {
                this.endCombat('draw');
                return;
            }
        }
        
        setTimeout(() => {
            this.startTurn();
        }, 500);
    }
    
    updateCombatHeader() {
        const header = document.querySelector('.combat-title');
        if (header) {
            header.textContent = `⚔️ Combat - Turn ${this.currentCombat.turn}`;
        }
    }
    
    checkCombatEnd() {
        const aliveEnemies = this.currentCombat.enemies.filter(e => e.current_health > 0);
        const aliveParty = [...this.currentCombat.playerParty, ...this.currentCombat.allies]
            .filter(a => a.current_health > 0);
        
        if (aliveEnemies.length === 0) {
            this.endCombat('victory');
            return true;
        }
        
        if (aliveParty.length === 0) {
            this.endCombat('defeat');
            return true;
        }
        
        // Check turn limit
        if (this.currentCombat.data.turn_limit > 0 && this.currentCombat.turn > this.currentCombat.data.turn_limit) {
            this.endCombat('time_limit');
            return true;
        }
        
        return false;
    }
    
    endCombat(result) {
        this.isActive = false;
        
        // Store node references before closing combat
        const victoryNode = this.currentCombat?.data?.victory_node;
        const defeatNode = this.currentCombat?.data?.defeat_node;
        
        // Apply rewards if victory
        if (result === 'victory') {
            this.applyVictoryRewards();
            this.logCombatEvent('🎉 Victory! Combat rewards applied.');
            
            setTimeout(() => {
                this.closeCombat();
                if (victoryNode) {
                    renderNode(victoryNode);
                }
            }, 2000);
        } else if (result === 'defeat') {
            this.logCombatEvent('💀 Defeat! Your party has fallen...');
            
            setTimeout(() => {
                this.closeCombat();
                if (defeatNode) {
                    renderNode(defeatNode);
                }
            }, 2000);
        } else {
            this.logCombatEvent('⏰ Combat ended due to time limit.');
            
            setTimeout(() => {
                this.closeCombat();
            }, 2000);
        }
    }
    
    applyVictoryRewards() {
        const rewards = this.currentCombat.data;
        
        // Experience
        if (rewards.experience_reward) {
            this.currentCombat.playerParty.forEach(member => {
                // Apply experience (would integrate with character system)
                this.logCombatEvent(`${member.name} gains ${rewards.experience_reward} experience!`);
            });
        }
        
        // Gold
        if (rewards.gold_reward) {
            gameState.variables.gold = (gameState.variables.gold || 0) + rewards.gold_reward;
            this.logCombatEvent(`Gained ${rewards.gold_reward} gold!`);
        }
        
        // Items
        if (rewards.item_rewards && rewards.item_rewards.length > 0) {
            rewards.item_rewards.forEach(item => {
                player.inventory.push({ name: item.name, description: item.description || '' });
                this.logCombatEvent(`Found ${item.name}!`);
            });
        }
        
        // Update HUD
        updateHud();
    }
    
    attemptEscape() {
        const escapeChance = Math.random() * 20 + 1; // 1d20
        const difficulty = this.currentCombat.data.escape_difficulty || 10;
        
        if (escapeChance >= difficulty) {
            this.logCombatEvent('🏃 Successfully escaped from combat!');
            this.isActive = false;
            
            // Store escape node before closing combat
            const escapeNode = this.currentCombat?.data?.escape_node;
            
            setTimeout(() => {
                this.closeCombat();
                if (escapeNode) {
                    renderNode(escapeNode);
                }
            }, 1500);
        } else {
            this.logCombatEvent('🚫 Failed to escape! The turn is lost.');
            this.nextTurn();
        }
    }
    
    closeCombat() {
        const combatInterface = document.getElementById('advanced-combat-interface');
        if (combatInterface) {
            combatInterface.remove();
        }
        
        this.currentCombat = null;
        this.turnQueue = [];
        this.currentTurnIndex = 0;
    }
    
    animateDamage(target, damage, isCritical) {
        const element = document.getElementById(`combatant-${target.id}`);
        if (!element) return;
        
        // Create damage number
        const damageNumber = document.createElement('div');
        damageNumber.className = `damage-number ${isCritical ? 'critical' : ''}`;
        damageNumber.textContent = `-${damage}`;
        damageNumber.style.position = 'absolute';
        damageNumber.style.color = isCritical ? '#ff0000' : '#ff6666';
        damageNumber.style.fontWeight = 'bold';
        damageNumber.style.fontSize = isCritical ? '1.5em' : '1.2em';
        damageNumber.style.pointerEvents = 'none';
        damageNumber.style.zIndex = '1000';
        
        element.appendChild(damageNumber);
        
        // Animate
        element.classList.add('damage-flash');
        setTimeout(() => {
            element.classList.remove('damage-flash');
            if (damageNumber.parentNode) {
                damageNumber.remove();
            }
        }, 1000);
    }
    
    animateHealing(target, healing) {
        const element = document.getElementById(`combatant-${target.id}`);
        if (!element) return;
        
        // Create healing number
        const healingNumber = document.createElement('div');
        healingNumber.className = 'healing-number';
        healingNumber.textContent = `+${healing}`;
        healingNumber.style.position = 'absolute';
        healingNumber.style.color = '#00ff00';
        healingNumber.style.fontWeight = 'bold';
        healingNumber.style.fontSize = '1.2em';
        healingNumber.style.pointerEvents = 'none';
        healingNumber.style.zIndex = '1000';
        
        element.appendChild(healingNumber);
        
        // Animate
        element.classList.add('healing-flash');
        setTimeout(() => {
            element.classList.remove('healing-flash');
            if (healingNumber.parentNode) {
                healingNumber.remove();
            }
        }, 1000);
    }
    
    logCombatEvent(message) {
        const logElement = document.getElementById('combat-log');
        if (!logElement) return;
        
        const entry = document.createElement('div');
        entry.className = 'log-entry';
        entry.textContent = message;
        
        logElement.appendChild(entry);
        logElement.scrollTop = logElement.scrollHeight;
        
        // Keep log manageable
        while (logElement.children.length > 20) {
            logElement.removeChild(logElement.firstChild);
        }
    }
    
    processEnvironmentalEffects() {
        this.currentCombat.environmental_effects.forEach(effect => {
            // Process environmental hazards each turn
            this.logCombatEvent(`Environmental effect: ${effect.description}`);
        });
    }
    
    updateEnvironmentalEffects() {
        const effectsContainer = document.getElementById('environmental-effects');
        if (!effectsContainer) return;
        
        effectsContainer.innerHTML = '';
        this.currentCombat.environmental_effects.forEach(effect => {
            const effectElement = document.createElement('div');
            effectElement.className = 'environmental-effect';
            effectElement.innerHTML = `
                <span class="effect-icon">🌪️</span>
                <span class="effect-name">${effect.name}</span>
            `;
            effectsContainer.appendChild(effectElement);
        });
    }
}

// Combat AI class for enemy behavior
class CombatAI {
    constructor(aiType = "balanced") {
        this.type = aiType;
        this.behaviors = {
            aggressive: {
                attack_priority: 0.8,
                defense_priority: 0.1,
                support_priority: 0.1,
                target_preference: "lowest_health",
                risk_tolerance: "high"
            },
            defensive: {
                attack_priority: 0.3,
                defense_priority: 0.5,
                support_priority: 0.2,
                target_preference: "strongest",
                risk_tolerance: "low"
            },
            tactical: {
                attack_priority: 0.4,
                defense_priority: 0.3,
                support_priority: 0.3,
                target_preference: "strategic",
                risk_tolerance: "medium"
            },
            support: {
                attack_priority: 0.2,
                defense_priority: 0.2,
                support_priority: 0.6,
                target_preference: "ally_lowest_health",
                risk_tolerance: "medium"
            }
        };
        
        this.currentBehavior = this.behaviors[aiType] || this.behaviors.balanced;
    }
    
    chooseAction(actor, allies, enemies, battlefieldState) {
        const availableActions = this.getAvailableActions(actor);
        
        if (!availableActions.length) {
            return { type: 'wait', target: null };
        }
        
        // Score each action
        const actionScores = {};
        availableActions.forEach(action => {
            actionScores[action] = this.scoreAction(action, actor, allies, enemies, battlefieldState);
        });
        
        // Choose best action
        const bestAction = Object.keys(actionScores).reduce((a, b) => 
            actionScores[a] > actionScores[b] ? a : b
        );
        
        return this.formatAction(bestAction, actor, allies, enemies);
    }
    
    getAvailableActions(actor) {
        const actions = ['basic_attack'];
        
        // Add skills the actor can use
        (actor.skills || []).forEach(skillId => {
            if (this.canUseSkill(actor, skillId)) {
                actions.push(skillId);
            }
        });
        
        return actions;
    }
    
    canUseSkill(actor, skillId) {
        const skill = advancedCombat.skillDatabase.get(skillId);
        if (!skill) return false;
        
        return skill.mana_cost <= actor.current_mana;
    }
    
    scoreAction(action, actor, allies, enemies, battlefieldState) {
        let score = Math.random() * 10; // Base randomness
        
        const behavior = this.currentBehavior;
        const actorHealthRatio = actor.current_health / actor.max_health;
        
        // Basic attack scoring
        if (action === 'basic_attack') {
            score += behavior.attack_priority * 50;
            if (enemies.length > 0) score += 20;
        }
        
        // Skill-specific scoring
        const skill = advancedCombat.skillDatabase.get(action);
        if (skill) {
            if (skill.damage) {
                score += behavior.attack_priority * 60;
                if (skill.damage_type === 'fire' && battlefieldState.weather === 'dry') score += 10;
            }
            
            if (skill.healing) {
                score += behavior.support_priority * 70;
                if (actorHealthRatio < 0.5) score += 30;
            }
            
            if (skill.status_effects) {
                score += behavior.support_priority * 40;
            }
        }
        
        // Health-based modifiers
        if (actorHealthRatio < 0.3 && behavior.risk_tolerance === 'low') {
            if (skill && skill.healing) score += 40;
            if (action === 'basic_attack') score -= 20;
        }
        
        return score;
    }
    
    formatAction(action, actor, allies, enemies) {
        if (action === 'basic_attack') {
            const target = this.chooseTarget(enemies, this.currentBehavior.target_preference);
            return { type: 'attack', skill: 'basic_attack', target: target };
        }
        
        const skill = advancedCombat.skillDatabase.get(action);
        if (skill) {
            let target = null;
            
            if (skill.target_type === 'single_enemy') {
                target = this.chooseTarget(enemies, this.currentBehavior.target_preference);
            } else if (skill.target_type === 'single_ally') {
                target = this.chooseTarget([actor, ...allies], 'lowest_health');
            }
            
            return { type: 'attack', skill: action, target: target };
        }
        
        return { type: 'wait', target: null };
    }
    
    chooseTarget(targets, preference) {
        if (!targets || targets.length === 0) return null;
        
        switch (preference) {
            case 'lowest_health':
                return targets.reduce((min, target) => 
                    target.current_health < min.current_health ? target : min
                );
            case 'highest_health':
                return targets.reduce((max, target) => 
                    target.current_health > max.current_health ? target : max
                );
            case 'random':
                return targets[Math.floor(Math.random() * targets.length)];
            default:
                return targets[0];
        }
    }
}

// Global instance
const advancedCombat = new AdvancedCombatEngine();