const {
  Client,
  GatewayIntentBits,
  Partials,
  PermissionsBitField,
  REST,
  Routes,
  SlashCommandBuilder,
  EmbedBuilder,
  ActivityType,
  ActionRowBuilder,
  ButtonBuilder,
  ButtonStyle,
} = require("discord.js");
const fs = require("node:fs");
const path = require("node:path");

const TOKEN = process.env.DISCORD_TOKEN;
const CLIENT_ID = process.env.CLIENT_ID;
const CLIENT_SECRET = process.env.CLIENT_SECRET;
if (!TOKEN) throw new Error("DISCORD_TOKEN is required");
if (!CLIENT_ID) console.warn("CLIENT_ID is not configured; Discord.js will use the application id from the bot token.");
if (!CLIENT_SECRET) console.warn("CLIENT_SECRET is not used by the bot runtime; keep it configured for the dashboard OAuth integration.");

const DATA_FILE = path.join(__dirname, "sapphire-data.json");
const defaultGuild = () => ({
  welcomeEnabled: true,
  welcomeMessage: "Bienvenue {mention} dans {server} !",
  goodbyeEnabled: true,
  goodbyeMessage: "{username} a quitté le serveur.",
  welcomeChannelId: null,
  goodbyeChannelId: null,
  welcomeDm: false,
  autoRoleId: null,
  xpEnabled: true,
  xpRate: 1,
  xpCooldown: 60,
  antiRaidEnabled: true,
  raidThreshold: 8,
  raidWindow: 20,
  honeypotEnabled: false,
  honeypotChannelId: null,
  moderationLogEnabled: true,
  moderationLogChannelId: null,
  moderationActionMode: "log",
  whitelist: [],
  customCommands: {},
  lockdown: false,
  joinTimes: [],
});
const loadData = () => {
  try { return JSON.parse(fs.readFileSync(DATA_FILE, "utf8")); } catch { return { guilds: {}, users: {}, cases: [], akinator: {} }; }
};
const data = loadData();
const saveData = () => fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 2));
const guildData = (guildId) => { data.guilds[guildId] ??= defaultGuild(); return data.guilds[guildId]; };
const userData = (guildId, userId) => { data.users[guildId] ??= {}; data.users[guildId][userId] ??= { xp: 0, level: 0, messages: 0 }; return data.users[guildId][userId]; };
const render = (text, member) => String(text || "").replaceAll("{user}", String(member)).replaceAll("{username}", member.displayName).replaceAll("{server}", member.guild.name).replaceAll("{memberCount}", String(member.guild.memberCount)).replaceAll("{mention}", member.toString());
const levelForXp = (xp) => Math.floor(Math.sqrt(Math.max(0, xp) / 100));
const xpRequired = (level) => Math.pow(level + 1, 2) * 100;
const isAdmin = (interaction) => interaction.memberPermissions?.has(PermissionsBitField.Flags.Administrator);
const isModerator = (interaction) => interaction.memberPermissions?.has(PermissionsBitField.Flags.ManageMessages) || isAdmin(interaction);
const ephemeral = { flags: 64 };
const reply = (interaction, content) => interaction.replied || interaction.deferred ? interaction.followUp({ content, ...ephemeral }) : interaction.reply({ content, ...ephemeral });
const embed = (title, description, color = 0x5865f2) => new EmbedBuilder().setTitle(title).setDescription(description || "").setColor(color).setTimestamp();
const logCase = async (guild, targetId, moderatorId, action, reason) => {
  const item = { id: data.cases.length + 1, guildId: guild.id, targetId, moderatorId, action, reason, createdAt: new Date().toISOString() };
  data.cases.push(item); saveData();
  const cfg = guildData(guild.id);
  if (cfg.moderationLogEnabled && cfg.moderationLogChannelId) {
    const channel = await guild.channels.fetch(cfg.moderationLogChannelId).catch(() => null);
    if (channel?.isTextBased()) await channel.send({ embeds: [embed(`Cas #${item.id} · ${action}`, reason, 0xed4245).addFields({ name: "Membre", value: `<@${targetId}>`, inline: true }, { name: "Modérateur", value: `<@${moderatorId}>`, inline: true })] }).catch(() => {});
  }
  return item;
};
const command = (name, description) => new SlashCommandBuilder().setName(name).setDescription(description);
const commands = [
  command("help", "Afficher les commandes Sapphire"),
  command("settings", "Afficher les réglages du serveur"),
  command("serverinfo", "Afficher les informations du serveur"),
  command("userinfo", "Afficher les informations d’un membre").addUserOption(o => o.setName("member").setDescription("Membre").setRequired(false)),
  command("warn", "Avertir un membre").addUserOption(o => o.setName("member").setDescription("Membre").setRequired(true)).addStringOption(o => o.setName("reason").setDescription("Raison").setRequired(true)),
  command("timeout", "Mettre un membre en timeout").addUserOption(o => o.setName("member").setDescription("Membre").setRequired(true)).addIntegerOption(o => o.setName("minutes").setDescription("Durée en minutes").setMinValue(1).setMaxValue(40320).setRequired(true)).addStringOption(o => o.setName("reason").setDescription("Raison").setRequired(true)),
  command("kick", "Expulser un membre").addUserOption(o => o.setName("member").setDescription("Membre").setRequired(true)).addStringOption(o => o.setName("reason").setDescription("Raison").setRequired(true)),
  command("ban", "Bannir un membre").addUserOption(o => o.setName("member").setDescription("Membre").setRequired(true)).addStringOption(o => o.setName("reason").setDescription("Raison").setRequired(true)),
  command("case", "Afficher un cas de modération").addIntegerOption(o => o.setName("id").setDescription("Identifiant du cas").setRequired(true)),
  command("welcome", "Configurer le message d’accueil").addBooleanOption(o => o.setName("enabled").setDescription("Activer").setRequired(false)).addStringOption(o => o.setName("message").setDescription("Message").setRequired(false)),
  command("goodbye", "Configurer le message de départ").addBooleanOption(o => o.setName("enabled").setDescription("Activer").setRequired(false)).addStringOption(o => o.setName("message").setDescription("Message").setRequired(false)),
  command("autorole", "Définir le rôle automatique").addRoleOption(o => o.setName("role").setDescription("Rôle").setRequired(true)),
  command("welcomedm", "Activer ou désactiver le DM d’accueil").addBooleanOption(o => o.setName("enabled").setDescription("Activer").setRequired(true)),
  command("rank", "Afficher le rang XP").addUserOption(o => o.setName("member").setDescription("Membre").setRequired(false)),
  command("levels", "Activer ou désactiver les niveaux").addBooleanOption(o => o.setName("enabled").setDescription("Activer").setRequired(true)),
  command("leaderboard", "Afficher le classement XP"),
  command("setlevel", "Définir le niveau d’un membre").addUserOption(o => o.setName("member").setDescription("Membre").setRequired(true)).addIntegerOption(o => o.setName("level").setDescription("Niveau").setMinValue(0).setRequired(true)),
  command("addxp", "Ajouter de l’XP").addUserOption(o => o.setName("member").setDescription("Membre").setRequired(true)).addIntegerOption(o => o.setName("amount").setDescription("Montant").setMinValue(1).setRequired(true)),
  command("removexp", "Retirer de l’XP").addUserOption(o => o.setName("member").setDescription("Membre").setRequired(true)).addIntegerOption(o => o.setName("amount").setDescription("Montant").setMinValue(1).setRequired(true)),
  command("honeypot", "Configurer le canal honeypot").addChannelOption(o => o.setName("channel").setDescription("Canal").setRequired(true)),
  command("raid", "Configurer l’anti-raid").addBooleanOption(o => o.setName("enabled").setDescription("Activer").setRequired(true)).addIntegerOption(o => o.setName("threshold").setDescription("Seuil").setMinValue(2).setRequired(false)).addIntegerOption(o => o.setName("window").setDescription("Fenêtre en secondes").setMinValue(5).setRequired(false)),
  command("whitelist", "Ajouter un membre à la liste blanche").addUserOption(o => o.setName("member").setDescription("Membre").setRequired(true)),
  command("lockdown", "Activer ou désactiver le lockdown").addBooleanOption(o => o.setName("enabled").setDescription("Activer").setRequired(true)),
  command("logchannel", "Définir le canal de logs").addChannelOption(o => o.setName("channel").setDescription("Canal").setRequired(true)),
  command("customcommand", "Créer une commande personnalisée").addStringOption(o => o.setName("name").setDescription("Nom").setRequired(true)).addStringOption(o => o.setName("response").setDescription("Réponse").setRequired(true)),
  command("akinator", "Lancer un jeu de questions"),
  command("akinatorstats", "Afficher les statistiques Akinator"),
  command("akinatorleaderboard", "Afficher le classement Akinator"),
  command("role-add", "Ajouter un rôle").addUserOption(o => o.setName("member").setDescription("Membre").setRequired(true)).addRoleOption(o => o.setName("role").setDescription("Rôle").setRequired(true)),
  command("role-remove", "Retirer un rôle").addUserOption(o => o.setName("member").setDescription("Membre").setRequired(true)).addRoleOption(o => o.setName("role").setDescription("Rôle").setRequired(true)),
].map(c => c.toJSON());

const AKINATOR_QUESTIONS = [
  "Ton personnage est-il réel ?",
  "Ton personnage est-il connu pour la musique ?",
  "Ton personnage est-il un personnage de fiction ?",
  "Ton personnage vient-il d’un jeu vidéo ?",
  "Ton personnage est-il un héros ?",
];
const client = new Client({ intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildMembers, GatewayIntentBits.GuildMessages, GatewayIntentBits.MessageContent], partials: [Partials.GuildMember, Partials.Channel, Partials.Message] });
client.once("ready", async () => {
  console.log(`Sapphire connecté comme ${client.user.tag} dans ${client.guilds.cache.size} serveur(s)`);
  client.user.setActivity("/help | Sapphire", { type: ActivityType.Watching });
  await client.application.commands.set(commands).catch(error => console.error("Impossible de synchroniser les commandes:", error));
  console.log("Commandes slash synchronisées");
});
client.on("guildMemberAdd", async member => {
  const cfg = guildData(member.guild.id); cfg.joinTimes = (cfg.joinTimes || []).filter(t => Date.now() - t < cfg.raidWindow * 1000); cfg.joinTimes.push(Date.now());
  if (cfg.antiRaidEnabled && cfg.joinTimes.length >= cfg.raidThreshold && !cfg.lockdown) { cfg.lockdown = true; saveData(); }
  if (cfg.autoRoleId) await member.roles.add(cfg.autoRoleId).catch(() => {});
  if (cfg.welcomeEnabled) { const channel = cfg.welcomeChannelId ? await member.guild.channels.fetch(cfg.welcomeChannelId).catch(() => null) : member.guild.systemChannel; if (channel?.isTextBased()) await channel.send(render(cfg.welcomeMessage, member)).catch(() => {}); }
  if (cfg.welcomeDm) await member.send(render(cfg.welcomeMessage, member)).catch(() => {});
});
client.on("guildMemberRemove", async member => { const cfg = guildData(member.guild.id); if (!cfg.goodbyeEnabled) return; const channel = cfg.goodbyeChannelId ? await member.guild.channels.fetch(cfg.goodbyeChannelId).catch(() => null) : member.guild.systemChannel; if (channel?.isTextBased()) await channel.send(render(cfg.goodbyeMessage, member)).catch(() => {}); });
client.on("messageCreate", async message => {
  if (message.author.bot || !message.guild) return;
  const cfg = guildData(message.guild.id);
  if (cfg.honeypotEnabled && cfg.honeypotChannelId === message.channel.id && !message.member.permissions.has(PermissionsBitField.Flags.Administrator) && !cfg.whitelist.includes(message.author.id)) { await message.delete().catch(() => {}); await message.member.timeout(10 * 60 * 1000, "Honeypot").catch(() => {}); await logCase(message.guild, message.author.id, client.user.id, "honeypot", "Message dans le canal honeypot"); return; }
  const custom = cfg.customCommands?.[message.content.trim().toLowerCase()]; if (custom) await message.reply({ content: custom, allowedMentions: { parse: [] } });
  if (!cfg.xpEnabled) return; const u = userData(message.guild.id, message.author.id); const now = Date.now(); if (now - (u.lastXpAt || 0) < cfg.xpCooldown * 1000) return; u.lastXpAt = now; u.messages++; u.xp += Math.floor((5 + Math.random() * 11) * cfg.xpRate); const oldLevel = u.level; u.level = levelForXp(u.xp); if (u.level > oldLevel) await message.channel.send(`${message.member} atteint le niveau **${u.level}** !`).catch(() => {}); saveData();
});
client.on("interactionCreate", async interaction => {
  if (interaction.isButton()) {
    const [kind, userId, answer] = interaction.customId.split(":");
    if (kind !== "akinator" || userId !== interaction.user.id) return reply(interaction, "Cette partie ne t’appartient pas.");
    data.akinator ??= {};
    data.akinator[userId] ??= { games: 0, wins: 0 };
    const game = data.akinatorGames?.[userId];
    if (!game) return reply(interaction, "Cette partie a expiré. Relance `/akinator`.");
    game.answers.push(answer === "yes"); game.question += 1;
    if (game.question >= AKINATOR_QUESTIONS.length) {
      data.akinator[userId].games += 1; data.akinator[userId].wins += 1; delete data.akinatorGames[userId]; saveData();
      return interaction.update({ content: `J’ai trouvé ton personnage après ${AKINATOR_QUESTIONS.length} questions. Partie gagnée.`, components: [], embeds: [] });
    }
    saveData();
    const row = new ActionRowBuilder().addComponents(
      new ButtonBuilder().setCustomId(`akinator:${userId}:yes`).setLabel("Oui").setStyle(ButtonStyle.Success),
      new ButtonBuilder().setCustomId(`akinator:${userId}:no`).setLabel("Non").setStyle(ButtonStyle.Danger),
      new ButtonBuilder().setCustomId(`akinator:${userId}:maybe`).setLabel("Peut-être").setStyle(ButtonStyle.Secondary),
    );
    return interaction.update({ content: AKINATOR_QUESTIONS[game.question], components: [row] });
  }
  if (!interaction.isChatInputCommand() || !interaction.guild) return;
  const name = interaction.commandName; const cfg = guildData(interaction.guild.id);
  try {
    if (["warn", "timeout", "kick", "ban", "case"].includes(name) && !isModerator(interaction)) return reply(interaction, "Tu n’as pas la permission de modérer.");
    if (["welcome", "goodbye", "autorole", "welcomedm", "levels", "setlevel", "addxp", "removexp", "honeypot", "raid", "whitelist", "lockdown", "logchannel", "customcommand", "role-add", "role-remove"].includes(name) && !isAdmin(interaction) && !isModerator(interaction)) return reply(interaction, "Cette commande est réservée au personnel autorisé.");
    if (name === "help") return interaction.reply({ embeds: [embed("Sapphire", "Modération, accueil, niveaux XP, anti-raid, rôles et Akinator. Utilise `/` pour voir toutes les commandes.")] });
    if (name === "settings") return interaction.reply({ embeds: [embed("Réglages du serveur", `Accueil : **${cfg.welcomeEnabled ? "activé" : "désactivé"}**\nDépart : **${cfg.goodbyeEnabled ? "activé" : "désactivé"}**\nXP : **${cfg.xpEnabled ? "activé" : "désactivé"}**\nAnti-raid : **${cfg.antiRaidEnabled ? "activé" : "désactivé"}**\nHoneypot : **${cfg.honeypotEnabled ? "activé" : "désactivé"}**\nLogs : **${cfg.moderationLogEnabled ? "activés" : "désactivés"}**`)] });
    if (name === "serverinfo") return interaction.reply({ embeds: [embed(interaction.guild.name, `Membres : **${interaction.guild.memberCount}**\nSalons : **${interaction.guild.channels.cache.size}**\nCréé le : <t:${Math.floor(interaction.guild.createdTimestamp / 1000)}:D>`)] });
    if (name === "userinfo") { const m = interaction.options.getMember("member") || interaction.member; return interaction.reply({ embeds: [embed(m.user.tag, `ID : \`${m.id}\`\nCompte créé : <t:${Math.floor(m.user.createdTimestamp / 1000)}:D>\nRejoint : ${m.joinedTimestamp ? `<t:${Math.floor(m.joinedTimestamp / 1000)}:D>` : "inconnu"}`)] }); }
    if (["warn", "timeout", "kick", "ban"].includes(name)) { const m = interaction.options.getMember("member"); const reason = interaction.options.getString("reason"); if (!m || m.id === interaction.user.id) return reply(interaction, "Membre invalide."); if (m.roles.highest.position >= interaction.member.roles.highest.position && !isAdmin(interaction)) return reply(interaction, "La hiérarchie des rôles ne permet pas cette action."); if (name === "timeout") await m.timeout(interaction.options.getInteger("minutes") * 60 * 1000, reason); if (name === "kick") await m.kick(reason); if (name === "ban") await m.ban({ reason }); const c = await logCase(interaction.guild, m.id, interaction.user.id, name, reason); return interaction.reply({ embeds: [embed(`${name} effectué`, `Cas #${c.id} enregistré pour ${m.user.tag}.`, 0x57f287)] }); }
    if (name === "case") { const c = data.cases.find(x => x.guildId === interaction.guild.id && x.id === interaction.options.getInteger("id")); return c ? interaction.reply({ embeds: [embed(`Cas #${c.id}`, `Action : **${c.action}**\nCible : <@${c.targetId}>\nRaison : ${c.reason}\nDate : <t:${Math.floor(new Date(c.createdAt).getTime() / 1000)}:F>`)] }) : reply(interaction, "Cas introuvable."); }
    if (name === "welcome" || name === "goodbye") { const key = name === "welcome" ? "welcome" : "goodbye"; const enabled = interaction.options.getBoolean("enabled"); const message = interaction.options.getString("message"); if (enabled !== null) cfg[`${key}Enabled`] = enabled; if (message !== null) cfg[`${key}Message`] = message; saveData(); return reply(interaction, `${name} mis à jour.`); }
    if (name === "autorole") { cfg.autoRoleId = interaction.options.getRole("role").id; saveData(); return reply(interaction, "Rôle automatique enregistré."); }
    if (name === "welcomedm") { cfg.welcomeDm = interaction.options.getBoolean("enabled"); saveData(); return reply(interaction, "DM d’accueil mis à jour."); }
    if (name === "rank") { const m = interaction.options.getMember("member") || interaction.member; const u = userData(interaction.guild.id, m.id); return interaction.reply({ embeds: [embed(`Rang de ${m.displayName}`, `Niveau : **${u.level}**\nXP : **${u.xp} / ${xpRequired(u.level)}**\nMessages : **${u.messages}**`)] }); }
    if (name === "levels") { cfg.xpEnabled = interaction.options.getBoolean("enabled"); saveData(); return reply(interaction, `Système XP ${cfg.xpEnabled ? "activé" : "désactivé"}.`); }
    if (["setlevel", "addxp", "removexp"].includes(name)) { const m = interaction.options.getMember("member"); const u = userData(interaction.guild.id, m.id); const amount = interaction.options.getInteger(name === "setlevel" ? "level" : "amount"); if (name === "setlevel") u.level = amount, u.xp = amount * amount * 100; else u.xp = Math.max(0, u.xp + (name === "addxp" ? amount : -amount)), u.level = levelForXp(u.xp); saveData(); return reply(interaction, `Profil XP de ${m.displayName} mis à jour.`); }
    if (name === "leaderboard") { const rows = Object.entries(data.users[interaction.guild.id] || {}).sort((a, b) => b[1].xp - a[1].xp).slice(0, 10).map(([id, u], i) => `${i + 1}. <@${id}> — niveau ${u.level}, ${u.xp} XP`); return interaction.reply({ embeds: [embed("Classement XP", rows.join("\n") || "Aucun membre classé.")] }); }
    if (name === "honeypot") { cfg.honeypotEnabled = true; cfg.honeypotChannelId = interaction.options.getChannel("channel").id; saveData(); return reply(interaction, "Honeypot activé."); }
    if (name === "raid") { cfg.antiRaidEnabled = interaction.options.getBoolean("enabled"); cfg.raidThreshold = interaction.options.getInteger("threshold") || cfg.raidThreshold; cfg.raidWindow = interaction.options.getInteger("window") || cfg.raidWindow; saveData(); return reply(interaction, "Protection anti-raid mise à jour."); }
    if (name === "whitelist") { const id = interaction.options.getUser("member").id; if (!cfg.whitelist.includes(id)) cfg.whitelist.push(id); saveData(); return reply(interaction, "Membre ajouté à la liste blanche."); }
    if (name === "lockdown") { cfg.lockdown = interaction.options.getBoolean("enabled"); saveData(); return reply(interaction, `Lockdown ${cfg.lockdown ? "activé" : "désactivé"}.`); }
    if (name === "logchannel") { cfg.moderationLogChannelId = interaction.options.getChannel("channel").id; saveData(); return reply(interaction, "Canal de logs enregistré."); }
    if (name === "customcommand") { cfg.customCommands[interaction.options.getString("name").toLowerCase()] = interaction.options.getString("response"); saveData(); return reply(interaction, "Commande personnalisée enregistrée."); }
    if (name === "role-add" || name === "role-remove") { const m = interaction.options.getMember("member"); const role = interaction.options.getRole("role"); if (name === "role-add") await m.roles.add(role); else await m.roles.remove(role); return reply(interaction, "Rôle mis à jour."); }
    if (name === "akinator") {
      data.akinatorGames ??= {}; data.akinatorGames[interaction.user.id] = { question: 0, answers: [], startedAt: Date.now() }; saveData();
      const row = new ActionRowBuilder().addComponents(
        new ButtonBuilder().setCustomId(`akinator:${interaction.user.id}:yes`).setLabel("Oui").setStyle(ButtonStyle.Success),
        new ButtonBuilder().setCustomId(`akinator:${interaction.user.id}:no`).setLabel("Non").setStyle(ButtonStyle.Danger),
        new ButtonBuilder().setCustomId(`akinator:${interaction.user.id}:maybe`).setLabel("Peut-être").setStyle(ButtonStyle.Secondary),
      );
      return interaction.reply({ content: AKINATOR_QUESTIONS[0], components: [row] });
    }
    if (name === "akinatorstats") { const stats = data.akinator?.[interaction.user.id] || { games: 0, wins: 0 }; return interaction.reply({ embeds: [embed("Akinator", `Parties : **${stats.games}**\nParties gagnées : **${stats.wins}**`)] }); }
    if (name === "akinatorleaderboard") { const rows = Object.entries(data.akinator || {}).sort((a, b) => b[1].wins - a[1].wins).slice(0, 10).map(([id, stats], i) => `${i + 1}. <@${id}> — ${stats.wins} victoire(s)`); return interaction.reply({ embeds: [embed("Classement Akinator", rows.join("\n") || "Aucune partie enregistrée.")] }); }
  } catch (error) { console.error(`[Sapphire] ${name}`, error); if (!interaction.replied) await reply(interaction, "Une erreur est survenue. Vérifie les permissions du bot et de son rôle."); }
});
process.on("SIGTERM", () => { saveData(); client.destroy(); process.exit(0); });
process.on("SIGINT", () => { saveData(); client.destroy(); process.exit(0); });
client.login(TOKEN);
