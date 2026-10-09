// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'app_database.dart';

// ignore_for_file: type=lint
class $CachedSnapshotsTable extends CachedSnapshots
    with TableInfo<$CachedSnapshotsTable, CachedSnapshot> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $CachedSnapshotsTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _cacheKeyMeta = const VerificationMeta(
    'cacheKey',
  );
  @override
  late final GeneratedColumn<String> cacheKey = GeneratedColumn<String>(
    'cache_key',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _userIdMeta = const VerificationMeta('userId');
  @override
  late final GeneratedColumn<String> userId = GeneratedColumn<String>(
    'user_id',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _payloadMeta = const VerificationMeta(
    'payload',
  );
  @override
  late final GeneratedColumn<String> payload = GeneratedColumn<String>(
    'payload',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _fetchedAtMeta = const VerificationMeta(
    'fetchedAt',
  );
  @override
  late final GeneratedColumn<DateTime> fetchedAt = GeneratedColumn<DateTime>(
    'fetched_at',
    aliasedName,
    false,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: true,
  );
  @override
  List<GeneratedColumn> get $columns => [cacheKey, userId, payload, fetchedAt];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'cached_snapshots';
  @override
  VerificationContext validateIntegrity(
    Insertable<CachedSnapshot> instance, {
    bool isInserting = false,
  }) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('cache_key')) {
      context.handle(
        _cacheKeyMeta,
        cacheKey.isAcceptableOrUnknown(data['cache_key']!, _cacheKeyMeta),
      );
    } else if (isInserting) {
      context.missing(_cacheKeyMeta);
    }
    if (data.containsKey('user_id')) {
      context.handle(
        _userIdMeta,
        userId.isAcceptableOrUnknown(data['user_id']!, _userIdMeta),
      );
    } else if (isInserting) {
      context.missing(_userIdMeta);
    }
    if (data.containsKey('payload')) {
      context.handle(
        _payloadMeta,
        payload.isAcceptableOrUnknown(data['payload']!, _payloadMeta),
      );
    } else if (isInserting) {
      context.missing(_payloadMeta);
    }
    if (data.containsKey('fetched_at')) {
      context.handle(
        _fetchedAtMeta,
        fetchedAt.isAcceptableOrUnknown(data['fetched_at']!, _fetchedAtMeta),
      );
    } else if (isInserting) {
      context.missing(_fetchedAtMeta);
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {cacheKey};
  @override
  CachedSnapshot map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return CachedSnapshot(
      cacheKey: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}cache_key'],
      )!,
      userId: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}user_id'],
      )!,
      payload: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}payload'],
      )!,
      fetchedAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}fetched_at'],
      )!,
    );
  }

  @override
  $CachedSnapshotsTable createAlias(String alias) {
    return $CachedSnapshotsTable(attachedDatabase, alias);
  }
}

class CachedSnapshot extends DataClass implements Insertable<CachedSnapshot> {
  final String cacheKey;
  final String userId;
  final String payload;
  final DateTime fetchedAt;
  const CachedSnapshot({
    required this.cacheKey,
    required this.userId,
    required this.payload,
    required this.fetchedAt,
  });
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['cache_key'] = Variable<String>(cacheKey);
    map['user_id'] = Variable<String>(userId);
    map['payload'] = Variable<String>(payload);
    map['fetched_at'] = Variable<DateTime>(fetchedAt);
    return map;
  }

  CachedSnapshotsCompanion toCompanion(bool nullToAbsent) {
    return CachedSnapshotsCompanion(
      cacheKey: Value(cacheKey),
      userId: Value(userId),
      payload: Value(payload),
      fetchedAt: Value(fetchedAt),
    );
  }

  factory CachedSnapshot.fromJson(
    Map<String, dynamic> json, {
    ValueSerializer? serializer,
  }) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return CachedSnapshot(
      cacheKey: serializer.fromJson<String>(json['cacheKey']),
      userId: serializer.fromJson<String>(json['userId']),
      payload: serializer.fromJson<String>(json['payload']),
      fetchedAt: serializer.fromJson<DateTime>(json['fetchedAt']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'cacheKey': serializer.toJson<String>(cacheKey),
      'userId': serializer.toJson<String>(userId),
      'payload': serializer.toJson<String>(payload),
      'fetchedAt': serializer.toJson<DateTime>(fetchedAt),
    };
  }

  CachedSnapshot copyWith({
    String? cacheKey,
    String? userId,
    String? payload,
    DateTime? fetchedAt,
  }) => CachedSnapshot(
    cacheKey: cacheKey ?? this.cacheKey,
    userId: userId ?? this.userId,
    payload: payload ?? this.payload,
    fetchedAt: fetchedAt ?? this.fetchedAt,
  );
  CachedSnapshot copyWithCompanion(CachedSnapshotsCompanion data) {
    return CachedSnapshot(
      cacheKey: data.cacheKey.present ? data.cacheKey.value : this.cacheKey,
      userId: data.userId.present ? data.userId.value : this.userId,
      payload: data.payload.present ? data.payload.value : this.payload,
      fetchedAt: data.fetchedAt.present ? data.fetchedAt.value : this.fetchedAt,
    );
  }

  @override
  String toString() {
    return (StringBuffer('CachedSnapshot(')
          ..write('cacheKey: $cacheKey, ')
          ..write('userId: $userId, ')
          ..write('payload: $payload, ')
          ..write('fetchedAt: $fetchedAt')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(cacheKey, userId, payload, fetchedAt);
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is CachedSnapshot &&
          other.cacheKey == this.cacheKey &&
          other.userId == this.userId &&
          other.payload == this.payload &&
          other.fetchedAt == this.fetchedAt);
}

class CachedSnapshotsCompanion extends UpdateCompanion<CachedSnapshot> {
  final Value<String> cacheKey;
  final Value<String> userId;
  final Value<String> payload;
  final Value<DateTime> fetchedAt;
  final Value<int> rowid;
  const CachedSnapshotsCompanion({
    this.cacheKey = const Value.absent(),
    this.userId = const Value.absent(),
    this.payload = const Value.absent(),
    this.fetchedAt = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  CachedSnapshotsCompanion.insert({
    required String cacheKey,
    required String userId,
    required String payload,
    required DateTime fetchedAt,
    this.rowid = const Value.absent(),
  }) : cacheKey = Value(cacheKey),
       userId = Value(userId),
       payload = Value(payload),
       fetchedAt = Value(fetchedAt);
  static Insertable<CachedSnapshot> custom({
    Expression<String>? cacheKey,
    Expression<String>? userId,
    Expression<String>? payload,
    Expression<DateTime>? fetchedAt,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (cacheKey != null) 'cache_key': cacheKey,
      if (userId != null) 'user_id': userId,
      if (payload != null) 'payload': payload,
      if (fetchedAt != null) 'fetched_at': fetchedAt,
      if (rowid != null) 'rowid': rowid,
    });
  }

  CachedSnapshotsCompanion copyWith({
    Value<String>? cacheKey,
    Value<String>? userId,
    Value<String>? payload,
    Value<DateTime>? fetchedAt,
    Value<int>? rowid,
  }) {
    return CachedSnapshotsCompanion(
      cacheKey: cacheKey ?? this.cacheKey,
      userId: userId ?? this.userId,
      payload: payload ?? this.payload,
      fetchedAt: fetchedAt ?? this.fetchedAt,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (cacheKey.present) {
      map['cache_key'] = Variable<String>(cacheKey.value);
    }
    if (userId.present) {
      map['user_id'] = Variable<String>(userId.value);
    }
    if (payload.present) {
      map['payload'] = Variable<String>(payload.value);
    }
    if (fetchedAt.present) {
      map['fetched_at'] = Variable<DateTime>(fetchedAt.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('CachedSnapshotsCompanion(')
          ..write('cacheKey: $cacheKey, ')
          ..write('userId: $userId, ')
          ..write('payload: $payload, ')
          ..write('fetchedAt: $fetchedAt, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

class $OutboxTable extends Outbox with TableInfo<$OutboxTable, OutboxData> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $OutboxTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<int> id = GeneratedColumn<int>(
    'id',
    aliasedName,
    false,
    hasAutoIncrement: true,
    type: DriftSqlType.int,
    requiredDuringInsert: false,
    defaultConstraints: GeneratedColumn.constraintIsAlways(
      'PRIMARY KEY AUTOINCREMENT',
    ),
  );
  static const VerificationMeta _endpointMeta = const VerificationMeta(
    'endpoint',
  );
  @override
  late final GeneratedColumn<String> endpoint = GeneratedColumn<String>(
    'endpoint',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _methodMeta = const VerificationMeta('method');
  @override
  late final GeneratedColumn<String> method = GeneratedColumn<String>(
    'method',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _bodyMeta = const VerificationMeta('body');
  @override
  late final GeneratedColumn<String> body = GeneratedColumn<String>(
    'body',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _idempotencyKeyMeta = const VerificationMeta(
    'idempotencyKey',
  );
  @override
  late final GeneratedColumn<String> idempotencyKey = GeneratedColumn<String>(
    'idempotency_key',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _createdAtMeta = const VerificationMeta(
    'createdAt',
  );
  @override
  late final GeneratedColumn<DateTime> createdAt = GeneratedColumn<DateTime>(
    'created_at',
    aliasedName,
    false,
    type: DriftSqlType.dateTime,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _attemptsMeta = const VerificationMeta(
    'attempts',
  );
  @override
  late final GeneratedColumn<int> attempts = GeneratedColumn<int>(
    'attempts',
    aliasedName,
    false,
    type: DriftSqlType.int,
    requiredDuringInsert: false,
    defaultValue: const Constant(0),
  );
  static const VerificationMeta _lastErrorMeta = const VerificationMeta(
    'lastError',
  );
  @override
  late final GeneratedColumn<String> lastError = GeneratedColumn<String>(
    'last_error',
    aliasedName,
    true,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _statusMeta = const VerificationMeta('status');
  @override
  late final GeneratedColumn<String> status = GeneratedColumn<String>(
    'status',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
    defaultValue: const Constant('pending'),
  );
  @override
  List<GeneratedColumn> get $columns => [
    id,
    endpoint,
    method,
    body,
    idempotencyKey,
    createdAt,
    attempts,
    lastError,
    status,
  ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'outbox';
  @override
  VerificationContext validateIntegrity(
    Insertable<OutboxData> instance, {
    bool isInserting = false,
  }) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    }
    if (data.containsKey('endpoint')) {
      context.handle(
        _endpointMeta,
        endpoint.isAcceptableOrUnknown(data['endpoint']!, _endpointMeta),
      );
    } else if (isInserting) {
      context.missing(_endpointMeta);
    }
    if (data.containsKey('method')) {
      context.handle(
        _methodMeta,
        method.isAcceptableOrUnknown(data['method']!, _methodMeta),
      );
    } else if (isInserting) {
      context.missing(_methodMeta);
    }
    if (data.containsKey('body')) {
      context.handle(
        _bodyMeta,
        body.isAcceptableOrUnknown(data['body']!, _bodyMeta),
      );
    } else if (isInserting) {
      context.missing(_bodyMeta);
    }
    if (data.containsKey('idempotency_key')) {
      context.handle(
        _idempotencyKeyMeta,
        idempotencyKey.isAcceptableOrUnknown(
          data['idempotency_key']!,
          _idempotencyKeyMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_idempotencyKeyMeta);
    }
    if (data.containsKey('created_at')) {
      context.handle(
        _createdAtMeta,
        createdAt.isAcceptableOrUnknown(data['created_at']!, _createdAtMeta),
      );
    } else if (isInserting) {
      context.missing(_createdAtMeta);
    }
    if (data.containsKey('attempts')) {
      context.handle(
        _attemptsMeta,
        attempts.isAcceptableOrUnknown(data['attempts']!, _attemptsMeta),
      );
    }
    if (data.containsKey('last_error')) {
      context.handle(
        _lastErrorMeta,
        lastError.isAcceptableOrUnknown(data['last_error']!, _lastErrorMeta),
      );
    }
    if (data.containsKey('status')) {
      context.handle(
        _statusMeta,
        status.isAcceptableOrUnknown(data['status']!, _statusMeta),
      );
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};
  @override
  OutboxData map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return OutboxData(
      id: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}id'],
      )!,
      endpoint: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}endpoint'],
      )!,
      method: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}method'],
      )!,
      body: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}body'],
      )!,
      idempotencyKey: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}idempotency_key'],
      )!,
      createdAt: attachedDatabase.typeMapping.read(
        DriftSqlType.dateTime,
        data['${effectivePrefix}created_at'],
      )!,
      attempts: attachedDatabase.typeMapping.read(
        DriftSqlType.int,
        data['${effectivePrefix}attempts'],
      )!,
      lastError: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}last_error'],
      ),
      status: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}status'],
      )!,
    );
  }

  @override
  $OutboxTable createAlias(String alias) {
    return $OutboxTable(attachedDatabase, alias);
  }
}

class OutboxData extends DataClass implements Insertable<OutboxData> {
  final int id;
  final String endpoint;
  final String method;
  final String body;
  final String idempotencyKey;
  final DateTime createdAt;
  final int attempts;
  final String? lastError;
  final String status;
  const OutboxData({
    required this.id,
    required this.endpoint,
    required this.method,
    required this.body,
    required this.idempotencyKey,
    required this.createdAt,
    required this.attempts,
    this.lastError,
    required this.status,
  });
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<int>(id);
    map['endpoint'] = Variable<String>(endpoint);
    map['method'] = Variable<String>(method);
    map['body'] = Variable<String>(body);
    map['idempotency_key'] = Variable<String>(idempotencyKey);
    map['created_at'] = Variable<DateTime>(createdAt);
    map['attempts'] = Variable<int>(attempts);
    if (!nullToAbsent || lastError != null) {
      map['last_error'] = Variable<String>(lastError);
    }
    map['status'] = Variable<String>(status);
    return map;
  }

  OutboxCompanion toCompanion(bool nullToAbsent) {
    return OutboxCompanion(
      id: Value(id),
      endpoint: Value(endpoint),
      method: Value(method),
      body: Value(body),
      idempotencyKey: Value(idempotencyKey),
      createdAt: Value(createdAt),
      attempts: Value(attempts),
      lastError: lastError == null && nullToAbsent
          ? const Value.absent()
          : Value(lastError),
      status: Value(status),
    );
  }

  factory OutboxData.fromJson(
    Map<String, dynamic> json, {
    ValueSerializer? serializer,
  }) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return OutboxData(
      id: serializer.fromJson<int>(json['id']),
      endpoint: serializer.fromJson<String>(json['endpoint']),
      method: serializer.fromJson<String>(json['method']),
      body: serializer.fromJson<String>(json['body']),
      idempotencyKey: serializer.fromJson<String>(json['idempotencyKey']),
      createdAt: serializer.fromJson<DateTime>(json['createdAt']),
      attempts: serializer.fromJson<int>(json['attempts']),
      lastError: serializer.fromJson<String?>(json['lastError']),
      status: serializer.fromJson<String>(json['status']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<int>(id),
      'endpoint': serializer.toJson<String>(endpoint),
      'method': serializer.toJson<String>(method),
      'body': serializer.toJson<String>(body),
      'idempotencyKey': serializer.toJson<String>(idempotencyKey),
      'createdAt': serializer.toJson<DateTime>(createdAt),
      'attempts': serializer.toJson<int>(attempts),
      'lastError': serializer.toJson<String?>(lastError),
      'status': serializer.toJson<String>(status),
    };
  }

  OutboxData copyWith({
    int? id,
    String? endpoint,
    String? method,
    String? body,
    String? idempotencyKey,
    DateTime? createdAt,
    int? attempts,
    Value<String?> lastError = const Value.absent(),
    String? status,
  }) => OutboxData(
    id: id ?? this.id,
    endpoint: endpoint ?? this.endpoint,
    method: method ?? this.method,
    body: body ?? this.body,
    idempotencyKey: idempotencyKey ?? this.idempotencyKey,
    createdAt: createdAt ?? this.createdAt,
    attempts: attempts ?? this.attempts,
    lastError: lastError.present ? lastError.value : this.lastError,
    status: status ?? this.status,
  );
  OutboxData copyWithCompanion(OutboxCompanion data) {
    return OutboxData(
      id: data.id.present ? data.id.value : this.id,
      endpoint: data.endpoint.present ? data.endpoint.value : this.endpoint,
      method: data.method.present ? data.method.value : this.method,
      body: data.body.present ? data.body.value : this.body,
      idempotencyKey: data.idempotencyKey.present
          ? data.idempotencyKey.value
          : this.idempotencyKey,
      createdAt: data.createdAt.present ? data.createdAt.value : this.createdAt,
      attempts: data.attempts.present ? data.attempts.value : this.attempts,
      lastError: data.lastError.present ? data.lastError.value : this.lastError,
      status: data.status.present ? data.status.value : this.status,
    );
  }

  @override
  String toString() {
    return (StringBuffer('OutboxData(')
          ..write('id: $id, ')
          ..write('endpoint: $endpoint, ')
          ..write('method: $method, ')
          ..write('body: $body, ')
          ..write('idempotencyKey: $idempotencyKey, ')
          ..write('createdAt: $createdAt, ')
          ..write('attempts: $attempts, ')
          ..write('lastError: $lastError, ')
          ..write('status: $status')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
    id,
    endpoint,
    method,
    body,
    idempotencyKey,
    createdAt,
    attempts,
    lastError,
    status,
  );
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is OutboxData &&
          other.id == this.id &&
          other.endpoint == this.endpoint &&
          other.method == this.method &&
          other.body == this.body &&
          other.idempotencyKey == this.idempotencyKey &&
          other.createdAt == this.createdAt &&
          other.attempts == this.attempts &&
          other.lastError == this.lastError &&
          other.status == this.status);
}

class OutboxCompanion extends UpdateCompanion<OutboxData> {
  final Value<int> id;
  final Value<String> endpoint;
  final Value<String> method;
  final Value<String> body;
  final Value<String> idempotencyKey;
  final Value<DateTime> createdAt;
  final Value<int> attempts;
  final Value<String?> lastError;
  final Value<String> status;
  const OutboxCompanion({
    this.id = const Value.absent(),
    this.endpoint = const Value.absent(),
    this.method = const Value.absent(),
    this.body = const Value.absent(),
    this.idempotencyKey = const Value.absent(),
    this.createdAt = const Value.absent(),
    this.attempts = const Value.absent(),
    this.lastError = const Value.absent(),
    this.status = const Value.absent(),
  });
  OutboxCompanion.insert({
    this.id = const Value.absent(),
    required String endpoint,
    required String method,
    required String body,
    required String idempotencyKey,
    required DateTime createdAt,
    this.attempts = const Value.absent(),
    this.lastError = const Value.absent(),
    this.status = const Value.absent(),
  }) : endpoint = Value(endpoint),
       method = Value(method),
       body = Value(body),
       idempotencyKey = Value(idempotencyKey),
       createdAt = Value(createdAt);
  static Insertable<OutboxData> custom({
    Expression<int>? id,
    Expression<String>? endpoint,
    Expression<String>? method,
    Expression<String>? body,
    Expression<String>? idempotencyKey,
    Expression<DateTime>? createdAt,
    Expression<int>? attempts,
    Expression<String>? lastError,
    Expression<String>? status,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (endpoint != null) 'endpoint': endpoint,
      if (method != null) 'method': method,
      if (body != null) 'body': body,
      if (idempotencyKey != null) 'idempotency_key': idempotencyKey,
      if (createdAt != null) 'created_at': createdAt,
      if (attempts != null) 'attempts': attempts,
      if (lastError != null) 'last_error': lastError,
      if (status != null) 'status': status,
    });
  }

  OutboxCompanion copyWith({
    Value<int>? id,
    Value<String>? endpoint,
    Value<String>? method,
    Value<String>? body,
    Value<String>? idempotencyKey,
    Value<DateTime>? createdAt,
    Value<int>? attempts,
    Value<String?>? lastError,
    Value<String>? status,
  }) {
    return OutboxCompanion(
      id: id ?? this.id,
      endpoint: endpoint ?? this.endpoint,
      method: method ?? this.method,
      body: body ?? this.body,
      idempotencyKey: idempotencyKey ?? this.idempotencyKey,
      createdAt: createdAt ?? this.createdAt,
      attempts: attempts ?? this.attempts,
      lastError: lastError ?? this.lastError,
      status: status ?? this.status,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (id.present) {
      map['id'] = Variable<int>(id.value);
    }
    if (endpoint.present) {
      map['endpoint'] = Variable<String>(endpoint.value);
    }
    if (method.present) {
      map['method'] = Variable<String>(method.value);
    }
    if (body.present) {
      map['body'] = Variable<String>(body.value);
    }
    if (idempotencyKey.present) {
      map['idempotency_key'] = Variable<String>(idempotencyKey.value);
    }
    if (createdAt.present) {
      map['created_at'] = Variable<DateTime>(createdAt.value);
    }
    if (attempts.present) {
      map['attempts'] = Variable<int>(attempts.value);
    }
    if (lastError.present) {
      map['last_error'] = Variable<String>(lastError.value);
    }
    if (status.present) {
      map['status'] = Variable<String>(status.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('OutboxCompanion(')
          ..write('id: $id, ')
          ..write('endpoint: $endpoint, ')
          ..write('method: $method, ')
          ..write('body: $body, ')
          ..write('idempotencyKey: $idempotencyKey, ')
          ..write('createdAt: $createdAt, ')
          ..write('attempts: $attempts, ')
          ..write('lastError: $lastError, ')
          ..write('status: $status')
          ..write(')'))
        .toString();
  }
}

abstract class _$AppDatabase extends GeneratedDatabase {
  _$AppDatabase(QueryExecutor e) : super(e);
  $AppDatabaseManager get managers => $AppDatabaseManager(this);
  late final $CachedSnapshotsTable cachedSnapshots = $CachedSnapshotsTable(
    this,
  );
  late final $OutboxTable outbox = $OutboxTable(this);
  @override
  Iterable<TableInfo<Table, Object?>> get allTables =>
      allSchemaEntities.whereType<TableInfo<Table, Object?>>();
  @override
  List<DatabaseSchemaEntity> get allSchemaEntities => [cachedSnapshots, outbox];
}

typedef $$CachedSnapshotsTableCreateCompanionBuilder =
    CachedSnapshotsCompanion Function({
      required String cacheKey,
      required String userId,
      required String payload,
      required DateTime fetchedAt,
      Value<int> rowid,
    });
typedef $$CachedSnapshotsTableUpdateCompanionBuilder =
    CachedSnapshotsCompanion Function({
      Value<String> cacheKey,
      Value<String> userId,
      Value<String> payload,
      Value<DateTime> fetchedAt,
      Value<int> rowid,
    });

class $$CachedSnapshotsTableFilterComposer
    extends Composer<_$AppDatabase, $CachedSnapshotsTable> {
  $$CachedSnapshotsTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get cacheKey => $composableBuilder(
    column: $table.cacheKey,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get userId => $composableBuilder(
    column: $table.userId,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get payload => $composableBuilder(
    column: $table.payload,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get fetchedAt => $composableBuilder(
    column: $table.fetchedAt,
    builder: (column) => ColumnFilters(column),
  );
}

class $$CachedSnapshotsTableOrderingComposer
    extends Composer<_$AppDatabase, $CachedSnapshotsTable> {
  $$CachedSnapshotsTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get cacheKey => $composableBuilder(
    column: $table.cacheKey,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get userId => $composableBuilder(
    column: $table.userId,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get payload => $composableBuilder(
    column: $table.payload,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get fetchedAt => $composableBuilder(
    column: $table.fetchedAt,
    builder: (column) => ColumnOrderings(column),
  );
}

class $$CachedSnapshotsTableAnnotationComposer
    extends Composer<_$AppDatabase, $CachedSnapshotsTable> {
  $$CachedSnapshotsTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get cacheKey =>
      $composableBuilder(column: $table.cacheKey, builder: (column) => column);

  GeneratedColumn<String> get userId =>
      $composableBuilder(column: $table.userId, builder: (column) => column);

  GeneratedColumn<String> get payload =>
      $composableBuilder(column: $table.payload, builder: (column) => column);

  GeneratedColumn<DateTime> get fetchedAt =>
      $composableBuilder(column: $table.fetchedAt, builder: (column) => column);
}

class $$CachedSnapshotsTableTableManager
    extends
        RootTableManager<
          _$AppDatabase,
          $CachedSnapshotsTable,
          CachedSnapshot,
          $$CachedSnapshotsTableFilterComposer,
          $$CachedSnapshotsTableOrderingComposer,
          $$CachedSnapshotsTableAnnotationComposer,
          $$CachedSnapshotsTableCreateCompanionBuilder,
          $$CachedSnapshotsTableUpdateCompanionBuilder,
          (
            CachedSnapshot,
            BaseReferences<
              _$AppDatabase,
              $CachedSnapshotsTable,
              CachedSnapshot
            >,
          ),
          CachedSnapshot,
          PrefetchHooks Function()
        > {
  $$CachedSnapshotsTableTableManager(
    _$AppDatabase db,
    $CachedSnapshotsTable table,
  ) : super(
        TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$CachedSnapshotsTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$CachedSnapshotsTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$CachedSnapshotsTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback:
              ({
                Value<String> cacheKey = const Value.absent(),
                Value<String> userId = const Value.absent(),
                Value<String> payload = const Value.absent(),
                Value<DateTime> fetchedAt = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => CachedSnapshotsCompanion(
                cacheKey: cacheKey,
                userId: userId,
                payload: payload,
                fetchedAt: fetchedAt,
                rowid: rowid,
              ),
          createCompanionCallback:
              ({
                required String cacheKey,
                required String userId,
                required String payload,
                required DateTime fetchedAt,
                Value<int> rowid = const Value.absent(),
              }) => CachedSnapshotsCompanion.insert(
                cacheKey: cacheKey,
                userId: userId,
                payload: payload,
                fetchedAt: fetchedAt,
                rowid: rowid,
              ),
          withReferenceMapper: (p0) => p0
              .map(
                (e) => (
                  e.readTable<$CachedSnapshotsTable, CachedSnapshot>(table),
                  BaseReferences<
                    _$AppDatabase,
                    $CachedSnapshotsTable,
                    CachedSnapshot
                  >(db, table, e),
                ),
              )
              .toList(),
          prefetchHooksCallback: null,
        ),
      );
}

typedef $$CachedSnapshotsTableProcessedTableManager =
    ProcessedTableManager<
      _$AppDatabase,
      $CachedSnapshotsTable,
      CachedSnapshot,
      $$CachedSnapshotsTableFilterComposer,
      $$CachedSnapshotsTableOrderingComposer,
      $$CachedSnapshotsTableAnnotationComposer,
      $$CachedSnapshotsTableCreateCompanionBuilder,
      $$CachedSnapshotsTableUpdateCompanionBuilder,
      (
        CachedSnapshot,
        BaseReferences<_$AppDatabase, $CachedSnapshotsTable, CachedSnapshot>,
      ),
      CachedSnapshot,
      PrefetchHooks Function()
    >;
typedef $$OutboxTableCreateCompanionBuilder =
    OutboxCompanion Function({
      Value<int> id,
      required String endpoint,
      required String method,
      required String body,
      required String idempotencyKey,
      required DateTime createdAt,
      Value<int> attempts,
      Value<String?> lastError,
      Value<String> status,
    });
typedef $$OutboxTableUpdateCompanionBuilder =
    OutboxCompanion Function({
      Value<int> id,
      Value<String> endpoint,
      Value<String> method,
      Value<String> body,
      Value<String> idempotencyKey,
      Value<DateTime> createdAt,
      Value<int> attempts,
      Value<String?> lastError,
      Value<String> status,
    });

class $$OutboxTableFilterComposer
    extends Composer<_$AppDatabase, $OutboxTable> {
  $$OutboxTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<int> get id => $composableBuilder(
    column: $table.id,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get endpoint => $composableBuilder(
    column: $table.endpoint,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get method => $composableBuilder(
    column: $table.method,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get body => $composableBuilder(
    column: $table.body,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get idempotencyKey => $composableBuilder(
    column: $table.idempotencyKey,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<DateTime> get createdAt => $composableBuilder(
    column: $table.createdAt,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<int> get attempts => $composableBuilder(
    column: $table.attempts,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get lastError => $composableBuilder(
    column: $table.lastError,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get status => $composableBuilder(
    column: $table.status,
    builder: (column) => ColumnFilters(column),
  );
}

class $$OutboxTableOrderingComposer
    extends Composer<_$AppDatabase, $OutboxTable> {
  $$OutboxTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<int> get id => $composableBuilder(
    column: $table.id,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get endpoint => $composableBuilder(
    column: $table.endpoint,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get method => $composableBuilder(
    column: $table.method,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get body => $composableBuilder(
    column: $table.body,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get idempotencyKey => $composableBuilder(
    column: $table.idempotencyKey,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<DateTime> get createdAt => $composableBuilder(
    column: $table.createdAt,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<int> get attempts => $composableBuilder(
    column: $table.attempts,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get lastError => $composableBuilder(
    column: $table.lastError,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get status => $composableBuilder(
    column: $table.status,
    builder: (column) => ColumnOrderings(column),
  );
}

class $$OutboxTableAnnotationComposer
    extends Composer<_$AppDatabase, $OutboxTable> {
  $$OutboxTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<int> get id =>
      $composableBuilder(column: $table.id, builder: (column) => column);

  GeneratedColumn<String> get endpoint =>
      $composableBuilder(column: $table.endpoint, builder: (column) => column);

  GeneratedColumn<String> get method =>
      $composableBuilder(column: $table.method, builder: (column) => column);

  GeneratedColumn<String> get body =>
      $composableBuilder(column: $table.body, builder: (column) => column);

  GeneratedColumn<String> get idempotencyKey => $composableBuilder(
    column: $table.idempotencyKey,
    builder: (column) => column,
  );

  GeneratedColumn<DateTime> get createdAt =>
      $composableBuilder(column: $table.createdAt, builder: (column) => column);

  GeneratedColumn<int> get attempts =>
      $composableBuilder(column: $table.attempts, builder: (column) => column);

  GeneratedColumn<String> get lastError =>
      $composableBuilder(column: $table.lastError, builder: (column) => column);

  GeneratedColumn<String> get status =>
      $composableBuilder(column: $table.status, builder: (column) => column);
}

class $$OutboxTableTableManager
    extends
        RootTableManager<
          _$AppDatabase,
          $OutboxTable,
          OutboxData,
          $$OutboxTableFilterComposer,
          $$OutboxTableOrderingComposer,
          $$OutboxTableAnnotationComposer,
          $$OutboxTableCreateCompanionBuilder,
          $$OutboxTableUpdateCompanionBuilder,
          (OutboxData, BaseReferences<_$AppDatabase, $OutboxTable, OutboxData>),
          OutboxData,
          PrefetchHooks Function()
        > {
  $$OutboxTableTableManager(_$AppDatabase db, $OutboxTable table)
    : super(
        TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$OutboxTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$OutboxTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$OutboxTableAnnotationComposer($db: db, $table: table),
          updateCompanionCallback:
              ({
                Value<int> id = const Value.absent(),
                Value<String> endpoint = const Value.absent(),
                Value<String> method = const Value.absent(),
                Value<String> body = const Value.absent(),
                Value<String> idempotencyKey = const Value.absent(),
                Value<DateTime> createdAt = const Value.absent(),
                Value<int> attempts = const Value.absent(),
                Value<String?> lastError = const Value.absent(),
                Value<String> status = const Value.absent(),
              }) => OutboxCompanion(
                id: id,
                endpoint: endpoint,
                method: method,
                body: body,
                idempotencyKey: idempotencyKey,
                createdAt: createdAt,
                attempts: attempts,
                lastError: lastError,
                status: status,
              ),
          createCompanionCallback:
              ({
                Value<int> id = const Value.absent(),
                required String endpoint,
                required String method,
                required String body,
                required String idempotencyKey,
                required DateTime createdAt,
                Value<int> attempts = const Value.absent(),
                Value<String?> lastError = const Value.absent(),
                Value<String> status = const Value.absent(),
              }) => OutboxCompanion.insert(
                id: id,
                endpoint: endpoint,
                method: method,
                body: body,
                idempotencyKey: idempotencyKey,
                createdAt: createdAt,
                attempts: attempts,
                lastError: lastError,
                status: status,
              ),
          withReferenceMapper: (p0) => p0
              .map(
                (e) => (
                  e.readTable<$OutboxTable, OutboxData>(table),
                  BaseReferences<_$AppDatabase, $OutboxTable, OutboxData>(
                    db,
                    table,
                    e,
                  ),
                ),
              )
              .toList(),
          prefetchHooksCallback: null,
        ),
      );
}

typedef $$OutboxTableProcessedTableManager =
    ProcessedTableManager<
      _$AppDatabase,
      $OutboxTable,
      OutboxData,
      $$OutboxTableFilterComposer,
      $$OutboxTableOrderingComposer,
      $$OutboxTableAnnotationComposer,
      $$OutboxTableCreateCompanionBuilder,
      $$OutboxTableUpdateCompanionBuilder,
      (OutboxData, BaseReferences<_$AppDatabase, $OutboxTable, OutboxData>),
      OutboxData,
      PrefetchHooks Function()
    >;

class $AppDatabaseManager {
  final _$AppDatabase _db;
  $AppDatabaseManager(this._db);
  $$CachedSnapshotsTableTableManager get cachedSnapshots =>
      $$CachedSnapshotsTableTableManager(_db, _db.cachedSnapshots);
  $$OutboxTableTableManager get outbox =>
      $$OutboxTableTableManager(_db, _db.outbox);
}
