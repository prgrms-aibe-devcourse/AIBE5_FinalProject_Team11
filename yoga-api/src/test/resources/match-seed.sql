-- Seed data for MatchControllerIT
-- Pose 1: clean pose, no kill-switch contraindications, has a matching benefit
INSERT INTO poses (pose_id, canonical_name, common_name, difficulty_rank)
    VALUES ('warrior_ii', 'Virabhadrasana II', 'Warrior II', 2);

INSERT INTO pose_benefits (pose_id, tag, weight)
    VALUES ('warrior_ii', 'strength', 1.5),
           ('warrior_ii', 'balance', 1.0);

-- Pose 2: has a kill-switch contraindication for 'knee_injury'
INSERT INTO poses (pose_id, canonical_name, common_name, difficulty_rank)
    VALUES ('lotus', 'Padmasana', 'Lotus Pose', 3);

INSERT INTO pose_benefits (pose_id, tag, weight)
    VALUES ('lotus', 'flexibility', 2.0),
           ('lotus', 'strength', 0.5);

INSERT INTO pose_contraindications (pose_id, condition, severity, kill_switch, instruction)
    VALUES ('lotus', 'knee_injury', 'HIGH', TRUE,
            'Avoid full lotus with any knee injury — use easy pose instead.');
