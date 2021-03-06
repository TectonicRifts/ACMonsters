DELETE FROM `weenie` WHERE `class_Id` = 20;

INSERT INTO `weenie` (`class_Id`, `class_Name`, `type`, `last_Modified`)
VALUES (20, 'aurochbull', 10, '2020-08-13 11:27:09') /* Creature */;

INSERT INTO `weenie_properties_int` (`object_Id`, `type`, `value`)
VALUES (20,   1,         16) /* ItemType - Creature */
     , (20,   2,         11) /* CreatureType - Auroch */
     , (20,   3,         43) /* PaletteTemplate - LightBrown */
     , (20,   6,         -1) /* ItemsCapacity */
     , (20,   7,         -1) /* ContainersCapacity */
     , (20,  16,          1) /* ItemUseable - No */
     , (20,  25,          9) /* Level */
     , (20,  27,          0) /* ArmorType - None */
     , (20,  40,          2) /* CombatMode - Melee */
     , (20,  67,         64) /* Tolerance - Retaliate */
     , (20,  68,          5) /* TargetingTactic - Random, LastDamager */
     , (20,  72,         12) /* FriendType - Cow */
     , (20,  93,       1032) /* PhysicsState - ReportCollisions, Gravity */
     , (20, 133,          4) /* ShowableOnRadar - ShowAlways */
     , (20, 146,        420) /* XpOverride */;

INSERT INTO `weenie_properties_bool` (`object_Id`, `type`, `value`)
VALUES (20,   1, True ) /* Stuck */
     , (20,  11, False) /* IgnoreCollisions */
     , (20,  12, True ) /* ReportCollisions */
     , (20,  13, False) /* Ethereal */
     , (20,  14, True ) /* GravityStatus */
     , (20,  19, True ) /* Attackable */;

INSERT INTO `weenie_properties_float` (`object_Id`, `type`, `value`)
VALUES (20,   1,       5) /* HeartbeatInterval */
     , (20,   2,       0) /* HeartbeatTimestamp */
     , (20,   3, 0.10000000149011612) /* HealthRate */
     , (20,   4,       5) /* StaminaRate */
     , (20,   5,       2) /* ManaRate */
     , (20,  12,     0.5) /* Shade */
     , (20,  13, 0.3400000035762787) /* ArmorModVsSlash */
     , (20,  14, 0.18000000715255737) /* ArmorModVsPierce */
     , (20,  15, 0.03999999910593033) /* ArmorModVsBludgeon */
     , (20,  16, 0.18000000715255737) /* ArmorModVsCold */
     , (20,  17, 0.699999988079071) /* ArmorModVsFire */
     , (20,  18, 0.18000000715255737) /* ArmorModVsAcid */
     , (20,  19, 0.6000000238418579) /* ArmorModVsElectric */
     , (20,  31,      22) /* VisualAwarenessRange */
     , (20,  34,       4) /* PowerupTime */
     , (20,  36,       1) /* ChargeSpeed */
     , (20,  39, 1.100000023841858) /* DefaultScale */
     , (20,  64, 0.8600000143051147) /* ResistSlash */
     , (20,  65, 0.800000011920929) /* ResistPierce */
     , (20,  66,    0.75) /* ResistBludgeon */
     , (20,  67,       1) /* ResistFire */
     , (20,  68, 0.800000011920929) /* ResistCold */
     , (20,  69, 0.800000011920929) /* ResistAcid */
     , (20,  70,       1) /* ResistElectric */
     , (20,  71,       1) /* ResistHealthBoost */
     , (20,  72,       1) /* ResistStaminaDrain */
     , (20,  73,       1) /* ResistStaminaBoost */
     , (20,  74,       1) /* ResistManaDrain */
     , (20,  75,       1) /* ResistManaBoost */
     , (20, 104,      10) /* ObviousRadarRange */
     , (20, 125,       1) /* ResistHealthDrain */;

INSERT INTO `weenie_properties_string` (`object_Id`, `type`, `value`)
VALUES (20,   1, 'Auroch Bull') /* Name */;

INSERT INTO `weenie_properties_d_i_d` (`object_Id`, `type`, `value`)
VALUES (20,   1,   33554478) /* Setup */
     , (20,   2,  150994969) /* MotionTable */
     , (20,   3,  536870916) /* SoundTable */
     , (20,   4,  805306375) /* CombatTable */
     , (20,   6,   67109302) /* PaletteBase */
     , (20,   7,  268435548) /* ClothingBase */
     , (20,   8,  100667936) /* Icon */
     , (20,  22,  872415254) /* PhysicsEffectTable */
     , (20,  35,        459) /* DeathTreasureType - Loot Tier: 1 */;

INSERT INTO `weenie_properties_attribute` (`object_Id`, `type`, `init_Level`, `level_From_C_P`, `c_P_Spent`)
VALUES (20,   1, 135, 0, 0) /* Strength */
     , (20,   2, 130, 0, 0) /* Endurance */
     , (20,   3,  50, 0, 0) /* Quickness */
     , (20,   4,  50, 0, 0) /* Coordination */
     , (20,   5,  50, 0, 0) /* Focus */
     , (20,   6,  30, 0, 0) /* Self */;

INSERT INTO `weenie_properties_attribute_2nd` (`object_Id`, `type`, `init_Level`, `level_From_C_P`, `c_P_Spent`, `current_Level`)
VALUES (20,   1,     0, 0, 0, 65) /* MaxHealth */
     , (20,   3,     0, 0, 0, 130) /* MaxStamina */
     , (20,   5,     0, 0, 0, 30) /* MaxMana */;

INSERT INTO `weenie_properties_skill` (`object_Id`, `type`, `level_From_P_P`, `s_a_c`, `p_p`, `init_Level`, `resistance_At_Last_Check`, `last_Used_Time`)
VALUES (20,  6, 0, 3, 0,  50, 0, 0) /* MeleeDefense        Specialized */
     , (20,  7, 0, 3, 0,  92, 0, 0) /* MissileDefense      Specialized */
     , (20, 13, 0, 3, 0,  50, 0, 0) /* UnarmedCombat       Specialized */
     , (20, 15, 0, 3, 0,  17, 0, 0) /* MagicDefense        Specialized */
     , (20, 20, 0, 3, 0,  10, 0, 0) /* Deception           Specialized */
     , (20, 24, 0, 3, 0,  10, 0, 0) /* Run                 Specialized */;

INSERT INTO `weenie_properties_body_part` (`object_Id`, `key`, `d_Type`, `d_Val`, `d_Var`, `base_Armor`, `armor_Vs_Slash`, `armor_Vs_Pierce`, `armor_Vs_Bludgeon`, `armor_Vs_Cold`, `armor_Vs_Fire`, `armor_Vs_Acid`, `armor_Vs_Electric`, `armor_Vs_Nether`, `b_h`, `h_l_f`, `m_l_f`, `l_l_f`, `h_r_f`, `m_r_f`, `l_r_f`, `h_l_b`, `m_l_b`, `l_l_b`, `h_r_b`, `m_r_b`, `l_r_b`)
VALUES (20,  0,  4, 20, 0.75,   30,   10,    5,    1,    5,   21,    5,   18,    0, 1,  0.3,  0.2,    0,  0.3,  0.2,    0,    0,    0,    0,    0,    0,    0) /* Head */
     , (20,  9,  2, 20, 0.75,   40,   14,    7,    2,    7,   28,    7,   24,    0, 1,  0.2,    0,    0,  0.2,    0,    0,    0,    0,    0,    0,    0,    0) /* Horn */
     , (20, 10,  4,  0,    0,   15,    5,    3,    1,    3,   11,    3,    9,    0, 2,  0.2,  0.4,  0.5,  0.2,  0.4,  0.5,    0,    0,    0,    0,    0,    0) /* FrontLeg */
     , (20, 12,  4,  5,  0.3,   15,    5,    3,    1,    3,   11,    3,    9,    0, 3,    0,    0, 0.25,    0,    0, 0.25,    0,    0,    0,    0,    0,    0) /* FrontFoot */
     , (20, 13,  4,  0,    0,   15,    5,    3,    1,    3,   11,    3,    9,    0, 2,    0,    0,    0,    0,    0,    0,  0.3,  0.4,  0.5,  0.3,  0.4,  0.5) /* RearLeg */
     , (20, 15,  4,  3,  0.3,   15,    5,    3,    1,    3,   11,    3,    9,    0, 3,    0,    0,    0,    0,    0,    0,    0,    0, 0.25,    0,    0, 0.25) /* RearFoot */
     , (20, 16,  4,  0,    0,   20,    7,    4,    1,    4,   14,    4,   12,    0, 2,  0.3,  0.4, 0.25,  0.3,  0.4, 0.25,  0.6,  0.5, 0.25,  0.6,  0.5, 0.25) /* Torso */
     , (20, 17,  4,  1,  0.9,   15,    5,    3,    1,    3,   11,    3,    9,    0, 2,    0,    0,    0,    0,    0,    0,  0.1,  0.1,    0,  0.1,  0.1,    0) /* Tail */;

INSERT INTO `weenie_properties_emote` (`object_Id`, `category`, `probability`, `weenie_Class_Id`, `style`, `substyle`, `quest`, `vendor_Type`, `min_Health`, `max_Health`)
VALUES (20,  5 /* HeartBeat */,  0.025, NULL, 2147483709 /* NonCombat */, 1090519043 /* Ready */, NULL, NULL, NULL, NULL);

SET @parent_id = LAST_INSERT_ID();

INSERT INTO `weenie_properties_emote_action` (`emote_Id`, `order`, `type`, `delay`, `extent`, `motion`, `message`, `test_String`, `min`, `max`, `min_64`, `max_64`, `min_Dbl`, `max_Dbl`, `stat`, `display`, `amount`, `amount_64`, `hero_X_P_64`, `percent`, `spell_Id`, `wealth_Rating`, `treasure_Class`, `treasure_Type`, `p_Script`, `sound`, `destination_Type`, `weenie_Class_Id`, `stack_Size`, `palette`, `shade`, `try_To_Bond`, `obj_Cell_Id`, `origin_X`, `origin_Y`, `origin_Z`, `angles_W`, `angles_X`, `angles_Y`, `angles_Z`)
VALUES (@parent_id,  0,   5 /* Motion */, 0, 1, 268435537 /* Twitch1 */, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);

INSERT INTO `weenie_properties_emote` (`object_Id`, `category`, `probability`, `weenie_Class_Id`, `style`, `substyle`, `quest`, `vendor_Type`, `min_Health`, `max_Health`)
VALUES (20,  5 /* HeartBeat */,  0.025, NULL, 2147483708 /* HandCombat */, 1090519043 /* Ready */, NULL, NULL, NULL, NULL);

SET @parent_id = LAST_INSERT_ID();

INSERT INTO `weenie_properties_emote_action` (`emote_Id`, `order`, `type`, `delay`, `extent`, `motion`, `message`, `test_String`, `min`, `max`, `min_64`, `max_64`, `min_Dbl`, `max_Dbl`, `stat`, `display`, `amount`, `amount_64`, `hero_X_P_64`, `percent`, `spell_Id`, `wealth_Rating`, `treasure_Class`, `treasure_Type`, `p_Script`, `sound`, `destination_Type`, `weenie_Class_Id`, `stack_Size`, `palette`, `shade`, `try_To_Bond`, `obj_Cell_Id`, `origin_X`, `origin_Y`, `origin_Z`, `angles_W`, `angles_X`, `angles_Y`, `angles_Z`)
VALUES (@parent_id,  0,   5 /* Motion */, 0, 1, 268435537 /* Twitch1 */, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);

INSERT INTO `weenie_properties_emote` (`object_Id`, `category`, `probability`, `weenie_Class_Id`, `style`, `substyle`, `quest`, `vendor_Type`, `min_Health`, `max_Health`)
VALUES (20,  5 /* HeartBeat */,  0.125, NULL, 2147483708 /* HandCombat */, 1090519043 /* Ready */, NULL, NULL, NULL, NULL);

SET @parent_id = LAST_INSERT_ID();

INSERT INTO `weenie_properties_emote_action` (`emote_Id`, `order`, `type`, `delay`, `extent`, `motion`, `message`, `test_String`, `min`, `max`, `min_64`, `max_64`, `min_Dbl`, `max_Dbl`, `stat`, `display`, `amount`, `amount_64`, `hero_X_P_64`, `percent`, `spell_Id`, `wealth_Rating`, `treasure_Class`, `treasure_Type`, `p_Script`, `sound`, `destination_Type`, `weenie_Class_Id`, `stack_Size`, `palette`, `shade`, `try_To_Bond`, `obj_Cell_Id`, `origin_X`, `origin_Y`, `origin_Z`, `angles_W`, `angles_X`, `angles_Y`, `angles_Z`)
VALUES (@parent_id,  0,   5 /* Motion */, 0, 1, 268435538 /* Twitch2 */, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);

INSERT INTO `weenie_properties_emote` (`object_Id`, `category`, `probability`, `weenie_Class_Id`, `style`, `substyle`, `quest`, `vendor_Type`, `min_Health`, `max_Health`)
VALUES (20,  5 /* HeartBeat */,  0.125, NULL, 2147483709 /* NonCombat */, 1090519043 /* Ready */, NULL, NULL, NULL, NULL);

SET @parent_id = LAST_INSERT_ID();

INSERT INTO `weenie_properties_emote_action` (`emote_Id`, `order`, `type`, `delay`, `extent`, `motion`, `message`, `test_String`, `min`, `max`, `min_64`, `max_64`, `min_Dbl`, `max_Dbl`, `stat`, `display`, `amount`, `amount_64`, `hero_X_P_64`, `percent`, `spell_Id`, `wealth_Rating`, `treasure_Class`, `treasure_Type`, `p_Script`, `sound`, `destination_Type`, `weenie_Class_Id`, `stack_Size`, `palette`, `shade`, `try_To_Bond`, `obj_Cell_Id`, `origin_X`, `origin_Y`, `origin_Z`, `angles_W`, `angles_X`, `angles_Y`, `angles_Z`)
VALUES (@parent_id,  0,   5 /* Motion */, 0, 1, 268435538 /* Twitch2 */, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);

INSERT INTO `weenie_properties_create_list` (`object_Id`, `destination_Type`, `weenie_Class_Id`, `stack_Size`, `palette`, `shade`, `try_To_Bond`)
VALUES (20, 9,     0,  0, 0, 0.95, False) /* Create nothing for ContainTreasure */
     , (20, 9, 20857,  0, 0, 0.03, False) /* Create Cooking Stamp (20857) for ContainTreasure */
     , (20, 9,     0,  0, 0, 0.97, False) /* Create nothing for ContainTreasure */
     , (20, 9,   266,  0, 0, 0.05, False) /* Create Auroch Horn (266) for ContainTreasure */;
