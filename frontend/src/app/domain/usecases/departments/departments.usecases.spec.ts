import { describe, it, expect, beforeEach, vi } from 'vitest';
import { TestBed } from '@angular/core/testing';
import { firstValueFrom, of, throwError } from 'rxjs';
import { DepartmentRepository } from '@domain/repositories/department.repository';
import { Department } from '@domain/models/department.model';
import { DepartmentHasUsersError } from '@domain/models/department-errors';
import { GetDepartmentsUseCase } from './get-departments.usecase';
import { CreateDepartmentUseCase } from './create-department.usecase';
import { UpdateDepartmentUseCase } from './update-department.usecase';
import { DeleteDepartmentUseCase } from './delete-department.usecase';

const MOCK_DEPT: Department = { id: '1', name: 'Tecnología', userCount: 0 };

class MockDepartmentRepository implements DepartmentRepository {
  getAll = vi.fn().mockReturnValue(of([MOCK_DEPT]));
  create = vi.fn().mockReturnValue(of(MOCK_DEPT));
  update = vi.fn().mockReturnValue(of({ ...MOCK_DEPT, name: 'Ventas' }));
  delete = vi.fn().mockReturnValue(of(undefined));
}

describe('Department Use Cases', () => {
  let mockRepo: MockDepartmentRepository;

  beforeEach(() => {
    mockRepo = new MockDepartmentRepository();
    TestBed.configureTestingModule({
      providers: [
        GetDepartmentsUseCase,
        CreateDepartmentUseCase,
        UpdateDepartmentUseCase,
        DeleteDepartmentUseCase,
        { provide: DepartmentRepository, useValue: mockRepo },
      ],
    });
  });

  describe('GetDepartmentsUseCase', () => {
    it('returns all departments from repository', async () => {
      const useCase = TestBed.inject(GetDepartmentsUseCase);
      const result = await firstValueFrom(useCase.execute());
      expect(mockRepo.getAll).toHaveBeenCalledOnce();
      expect(result).toEqual([MOCK_DEPT]);
    });
  });

  describe('CreateDepartmentUseCase', () => {
    it('trims name before calling repository', async () => {
      const useCase = TestBed.inject(CreateDepartmentUseCase);
      await firstValueFrom(useCase.execute('  Tecnología  '));
      expect(mockRepo.create).toHaveBeenCalledWith('Tecnología');
    });

    it('throws error when name is empty after trimming', async () => {
      const useCase = TestBed.inject(CreateDepartmentUseCase);
      await expect(firstValueFrom(useCase.execute('   ')))
        .rejects.toThrow('Department name cannot be empty');
      expect(mockRepo.create).not.toHaveBeenCalled();
    });

    it('throws error when name is null or undefined', async () => {
      const useCase = TestBed.inject(CreateDepartmentUseCase);
      await expect(firstValueFrom(useCase.execute('' as unknown as string)))
        .rejects.toThrow('Department name cannot be empty');
      expect(mockRepo.create).not.toHaveBeenCalled();
    });
  });

  describe('UpdateDepartmentUseCase', () => {
    it('trims name before calling repository', async () => {
      const useCase = TestBed.inject(UpdateDepartmentUseCase);
      await firstValueFrom(useCase.execute('1', '  Ventas  '));
      expect(mockRepo.update).toHaveBeenCalledWith('1', 'Ventas');
    });

    it('throws error when name is empty after trimming', async () => {
      const useCase = TestBed.inject(UpdateDepartmentUseCase);
      await expect(firstValueFrom(useCase.execute('1', '   ')))
        .rejects.toThrow('Department name cannot be empty');
      expect(mockRepo.update).not.toHaveBeenCalled();
    });

    it('throws error when name is null or undefined', async () => {
      const useCase = TestBed.inject(UpdateDepartmentUseCase);
      await expect(firstValueFrom(useCase.execute('1', '' as unknown as string)))
        .rejects.toThrow('Department name cannot be empty');
      expect(mockRepo.update).not.toHaveBeenCalled();
    });
  });

  describe('DeleteDepartmentUseCase', () => {
    it('deletes a department with no users', async () => {
      const useCase = TestBed.inject(DeleteDepartmentUseCase);
      await firstValueFrom(useCase.execute({ ...MOCK_DEPT, userCount: 0 }));
      expect(mockRepo.delete).toHaveBeenCalledWith('1');
    });

    it('throws DepartmentHasUsersError when department has users', async () => {
      const useCase = TestBed.inject(DeleteDepartmentUseCase);
      mockRepo.delete.mockReturnValue(throwError(() => new DepartmentHasUsersError()));
      
      await expect(firstValueFrom(useCase.execute({ ...MOCK_DEPT, userCount: 3 })))
        .rejects.toThrow(DepartmentHasUsersError);
      expect(mockRepo.delete).not.toHaveBeenCalled();
    });
  });
});
